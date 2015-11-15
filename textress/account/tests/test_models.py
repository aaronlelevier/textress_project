import calendar
import datetime
import pytz

from django.db.models import Max, Sum
from django.test import TestCase, TransactionTestCase
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.utils import timezone

from model_mommy import mommy

from account.models import (Dates, Pricing, TransType, TransTypeCache, AcctCost, AcctStmt,
    AcctTrans, TRANS_TYPES, INIT_CHARGE_AMOUNT, CHARGE_AMOUNTS, BALANCE_AMOUNTS)
from account.tests.factory import (create_acct_stmts, create_acct_tran, create_acct_trans,
    create_trans_types)
from concierge.models import Guest, Message
from concierge.tests.factory import make_guests, make_messages
from main.models import Subaccount
from main.tests.factory import create_hotel, create_hotel_user, PASSWORD
from utils import create
from utils.exceptions import AutoRechargeOffExcp


class PricingTests(TestCase):
    # NOTE: Am skipping testing save() b/c these are static Pricing Tiers
    #   that are created once and hardly ever changed.

    fixtures = ['pricing.json']

    def test_fixtures(self):
        free_price = Pricing.objects.get(tier_name="Free")
        self.assertIsInstance(free_price, Pricing)

    ### No MTD SMS tests

    def test_cost(self):
        self.assertEqual(Pricing.objects.get_cost(units=200, units_mtd=0), 0)

    def test_cost_two_tiers(self):
        tier1 = 200 * 0
        tier2 = 100 * 5.5
        result = tier1 + tier2 # 550
        self.assertEqual(Pricing.objects.get_cost(units=300, units_mtd=0), -result)

    def test_cost_three_tiers(self):
        tier1 = 200 * 0
        tier2 = 2000 * 5.5
        tier3 = 300 * 5.25
        result = tier1 + tier2 + tier3 # 12575
        self.assertEqual(Pricing.objects.get_cost(units=2500, units_mtd=0), -result)

    ### MTD SMS tests

    def test_cost_mtd(self):
        result = 100 * 5.5
        self.assertEqual(Pricing.objects.get_cost(units=100, units_mtd=200), -result)

    def test_cost_mtd_two_tiers(self):
        tier1 = 200 * 5.5
        tier2 = 300 * 5.25
        result = tier1 + tier2
        self.assertEqual(Pricing.objects.get_cost(units=500, units_mtd=2000), -result)

    def test_cost_mtd_three_tiers(self):
        tier1 = 100 * 0
        tier2 = 2000 * 5.5
        tier3 = 400 * 5.25
        result = tier1 + tier2 + tier3
        self.assertEqual(Pricing.objects.get_cost(units=2500, units_mtd=100), -result)


class TransTypeTests(TestCase):
    # Test contains all TransTypes
    # This Model is also static (like the `Pricing` Model) and does not change.

    fixtures = ['trans_type.json']

    def test_types(self):
        init_amt = TransType.objects.get(name='init_amt')
        recharge_amt = TransType.objects.get(name='recharge_amt')
        sms_used = TransType.objects.get(name='sms_used')
        phone_number = TransType.objects.get(name='phone_number')

        self.assertIsInstance(init_amt, TransType)
        self.assertEqual(str(init_amt), init_amt.name)
        self.assertEqual(TransType.objects.count(), 4)


class TransTypeCacheTests(TestCase):

    fixtures = ['trans_type.json']

    def setUp(self):
        self.cache = TransTypeCache()

    def test_get_or_set_value(self):
        cache.clear()

        sms_used = self.cache.get_or_set_value('sms_used')

        self.assertIsInstance(sms_used, TransType)
        self.assertEqual(sms_used.name, 'sms_used')

    def test_cached_trans_types(self):
        trans_types = [x[0] for x in TRANS_TYPES]
        for t in trans_types:
            cache.clear()

            obj = getattr(self.cache, t)

            self.assertIsInstance(obj, TransType)
            self.assertEqual(obj.name, t)


class AcctCostTests(TestCase):
    '''
    Hotel can only have 1 AcctCost record. Can be updated.
    '''

    def setUp(self):
        self.hotel = create_hotel()
        # "other_hotel" has no affect on this one
        self.hotel_2 = create_hotel()
        AcctCost.objects.get_or_create(hotel=self.hotel_2)

    def test_create(self):
        # If a ``get_or_create`` is called w/ no kwargs, it returns the current
        # ``acct_cost`` as is
        acct_cost, created = AcctCost.objects.get_or_create(hotel=self.hotel)
        self.assertTrue(created)

        new_acct_cost, created = AcctCost.objects.get_or_create(hotel=self.hotel)
        self.assertFalse(created)
        self.assertEqual(acct_cost, new_acct_cost)
        self.assertEqual(AcctCost.objects.filter(hotel=self.hotel).count(), 1)
        self.assertEqual(acct_cost.balance_min, BALANCE_AMOUNTS[0][0])
        self.assertEqual(acct_cost.recharge_amt, CHARGE_AMOUNTS[0][0])

    def test_update_already_created(self):
        # create new actually modifies original b/c p/ Hotel, singleton obj
        acct_cost, created = AcctCost.objects.get_or_create(hotel=self.hotel)
        self.assertTrue(created)

        new_acct_cost, created = AcctCost.objects.get_or_create(
            hotel=self.hotel,
            balance_min=BALANCE_AMOUNTS[2][0],
            recharge_amt=CHARGE_AMOUNTS[2][0]
            )
        self.assertFalse(created)
        self.assertEqual(acct_cost, new_acct_cost)
        self.assertEqual(AcctCost.objects.filter(hotel=self.hotel).count(), 1)
        self.assertEqual(new_acct_cost.balance_min, BALANCE_AMOUNTS[2][0])
        self.assertEqual(new_acct_cost.recharge_amt, CHARGE_AMOUNTS[2][0])

    def test_init_charge_amount(self):
        acct_cost, created = AcctCost.objects.get_or_create(hotel=self.hotel)
        self.assertTrue(created)
        self.assertIsInstance(acct_cost, AcctCost)
        self.assertEqual(acct_cost.init_amt, INIT_CHARGE_AMOUNT)
        self.assertEqual(acct_cost.recharge_amt, INIT_CHARGE_AMOUNT)


class AcctStmtTests(TestCase):

    fixtures = ['pricing.json', 'trans_type.json']

    def setUp(self):
        self.password = PASSWORD
        self.today = timezone.now().date()
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, 'admin')
        
        # Guests (makes 10)
        self.guest = make_guests(hotel=self.hotel, number=1)[0] #b/c returns a list
        # Messages (makes 10)
        self.messages = make_messages(
            hotel=self.hotel,
            user=self.admin,
            guest=self.guest
            )

        # AcctStmt
        self.acct_stmts = create_acct_stmts(hotel=self.hotel)
        # Single AcctStmt
        self.acct_stmt = self.acct_stmts[0]
        # Supporting Models
        self.acct_cost = AcctCost.objects.get_or_create(hotel=self.hotel)
        self.acct_trans = create_acct_trans(hotel=self.hotel)

    ### MODEL TESTS

    def test_get_absolute_url(self):
        self.assertEqual(
            self.acct_stmt.get_absolute_url(),
            reverse('acct_stmt_detail', kwargs={'year':self.acct_stmt.year,
                'month':self.acct_stmt.month})
        )

    def test_str(self):
        self.assertEqual(
            str(self.acct_stmt),
            "{} {}".format(calendar.month_name[self.acct_stmt.month], self.acct_stmt.year)
        )

    def test_month_abbr(self):
        self.assertEqual(
            self.acct_stmt.month_abbr,
            "{} {}".format(calendar.month_abbr[self.acct_stmt.month], self.acct_stmt.year)
        )

    ### MANAGER TESTS

    def test_get_or_create_current_month(self):
        # Should already exist
        acct_stmt, created = AcctStmt.objects.get_or_create(
            hotel=self.hotel,
            month=self.today.month,
            year=self.today.year
            )
        self.assertIsInstance(acct_stmt, AcctStmt)
        self.assertTrue(created)

        acct_stmt, created = AcctStmt.objects.get_or_create(
            hotel=self.hotel,
            month=self.today.month,
            year=self.today.year
            )
        self.assertIsInstance(acct_stmt, AcctStmt)
        self.assertFalse(created)


class AcctStmtSignupTests(TestCase):

    fixtures = ['pricing.json', 'trans_type.json']

    def setUp(self):
        self.hotel = create_hotel()
        self.init_amt = TransType.objects.get(name='init_amt')
        self.acct_cost, _ = AcctCost.objects.get_or_create(hotel=self.hotel)

    def test_initial_acct_stmt(self):
        acct_tran, _ = AcctTrans.objects.get_or_create(hotel=self.hotel,
            trans_type=self.init_amt)

        acct_stmt, _ = AcctStmt.objects.get_or_create(hotel=self.hotel)

        self.assertEqual(acct_stmt.hotel, self.hotel)
        self.assertEqual(acct_stmt.monthly_costs, settings.DEFAULT_MONTHLY_FEE)
        self.assertEqual(acct_stmt.total_sms, 0)
        self.assertEqual(acct_stmt.balance, self.acct_cost.init_amt) # Most important test!!
        self.assertEqual(
            acct_stmt.balance,
            AcctTrans.objects.balance(hotel=self.hotel)
        )


class AcctStmtNewHotelTests(TestCase):
    # Test Hotels that have only signed up, and don't have 
    # any SMS sent yet

    fixtures = ['trans_type.json']

    def setUp(self):
        self.password = PASSWORD
        # Dates
        date = Dates()
        self.today = date._today
        self.yesterday = date._yesterday
        # Users
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, 'admin')
        self.guest = make_guests(hotel=self.hotel, number=1)[0] #b/c returns a list
        # Supporting Models
        self.sms_used, _ = TransType.objects.get_or_create(name='sms_used')
        self.acct_cost, _ = AcctCost.objects.get_or_create(hotel=self.hotel)

    def test_sms_used_mtd(self):
        acct_stmt, created = AcctStmt.objects.get_or_create(hotel=self.hotel)
        self.assertIsInstance(acct_stmt,AcctStmt)
        self.assertEqual(AcctTrans.objects.sms_used_mtd(self.hotel, self.today), 0)


class AcctTransQuerySetTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.trans_types = create_trans_types()
        self.today = timezone.now().date()
        # TransType
        self.init_amt = TransType.objects.get(name='init_amt')
        self.sms_used = TransType.objects.get(name='sms_used')
        # AcctTrans
        self.acct_trans = create_acct_tran(
            hotel=self.hotel,
            trans_type=self.trans_types[0],
            insert_date=self.today
        )
        self.acct_trans2 = create_acct_tran(
            hotel=self.hotel,
            trans_type=self.init_amt,
            insert_date=self.today
        )
        # Hotel 2
        self.hotel2 = create_hotel()
        self.acct_trans = create_acct_tran(
            hotel=self.hotel2,
            trans_type=self.sms_used,
            insert_date=self.today,
            amount=1000
        )

    def test_monthly_trans(self):
        self.assertTrue(AcctTrans.objects.monthly_trans(self.hotel, self.today))

    def test_monthly_trans_default_date(self):
        monthly_trans = AcctTrans.objects.filter(
            hotel=self.hotel,
            insert_date__month=self.today.month,
            insert_date__year=self.today.year
        )

        monthly_trans_mgr = AcctTrans.objects.monthly_trans(hotel=self.hotel)

        self.assertEqual(monthly_trans.count(), monthly_trans_mgr.count())

    def test_balance(self):
        balance = AcctTrans.objects.balance()

        self.assertEqual(
            balance,
            AcctTrans.objects.aggregate(Sum('amount'))['amount__sum']
        )

    def test_balance_hotel(self):
        balance = AcctTrans.objects.balance(self.hotel)

        self.assertEqual(
            balance,
            AcctTrans.objects.filter(hotel=self.hotel).aggregate(Sum('amount'))['amount__sum']
        )


class AcctTransManagerTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.trans_types = create_trans_types()
        self.today = timezone.now().date()
        self.yesterday = self.today - datetime.timedelta(days=1)
        # AcctCost
        self.acct_cost = mommy.make(AcctCost, hotel=self.hotel)
        # TransType
        self.init_amt = TransType.objects.get(name='init_amt')
        self.sms_used = TransType.objects.get(name='sms_used')
        # AcctTrans
        self.acct_trans = create_acct_tran(
            hotel=self.hotel,
            trans_type=self.trans_types[0],
            insert_date=self.today
        )
        self.acct_trans2 = create_acct_tran(
            hotel=self.hotel,
            trans_type=self.init_amt,
            insert_date=self.today
        )
        # Hotel 2
        self.hotel2 = create_hotel()
        self.acct_trans = create_acct_tran(
            hotel=self.hotel2,
            trans_type=self.sms_used,
            insert_date=self.today,
            amount=1000
        )

    def test_get_balance(self):
        self.assertEqual(
            AcctTrans.objects.get_balance(self.hotel),
            AcctTrans.objects.filter(hotel=self.hotel).order_by('-modified').first().balance
        )

    def test_check_recharge_required_true(self):
        balance = self.acct_cost.balance_min - 1
        self.assertTrue(AcctTrans.objects.check_recharge_required(self.hotel, balance))

    def test_check_recharge_required_false(self):
        balance = self.acct_cost.balance_min + 1
        self.assertFalse(AcctTrans.objects.check_recharge_required(self.hotel, balance))

    def test_calculate_recharge_amount(self):
        balance = 100
        self.assertEqual(
            AcctTrans.objects.calculate_recharge_amount(self.hotel, balance),
            self.hotel.acct_cost.recharge_amt - balance
        )

    # sms_used_mtd_as_of_yesterday

    def test_sms_used_mtd_as_of_yesterday(self):
        self.assertEqual(AcctTrans.objects.filter(hotel=self.hotel,trans_type=self.sms_used).count(), 0)
        acct_trans = create_acct_tran(hotel=self.hotel, trans_type=self.sms_used,
                insert_date=self.yesterday)

        sms_used_count = AcctTrans.objects.sms_used_mtd_as_of_yesterday(self.hotel)

        # tests
        self.assertEqual(AcctTrans.objects.filter(hotel=self.hotel,trans_type=self.sms_used).count(), 1)

        if self.yesterday.month != self.today.month:
            self.assertEqual(sms_used_count, 0)

        self.assertEqual(acct_trans.sms_used, sms_used_count)

    def test_sms_used_mtd_as_of_yesterday_does_not_exist_returs_zero(self):
        # this test will be triggered on the 1st day of signup b/c not prior date records
        self.assertEqual(AcctTrans.objects.filter(hotel=self.hotel,trans_type=self.sms_used).count(), 0)

        sms_used_count = AcctTrans.objects.sms_used_mtd_as_of_yesterday(self.hotel)

        self.assertEqual(sms_used_count, 0)

    def test_sms_used_mtd_as_of_yesterday_aggregate(self):
        # for an aggreate of "sms_used_count" for the month we need at least 2 days
        if self.today.day >= 3:
            create_acct_tran(hotel=self.hotel, trans_type=self.sms_used,
                insert_date=self.yesterday)
            two_days_ago = self.yesterday - datetime.timedelta(days=1)
            create_acct_tran(hotel=self.hotel, trans_type=self.sms_used,
                insert_date=two_days_ago)

        sms_used_count = AcctTrans.objects.sms_used_mtd_as_of_yesterday(self.hotel)
        sms_used_manual_count = (AcctTrans.objects.filter(hotel=self.hotel,
                                                          insert_date__month=self.today.month,
                                                          insert_date__lte=self.today)
                                                   .aggregate(Sum('sms_used'))['sms_used__sum'])

        self.assertEqual(sms_used_count, sms_used_manual_count)


class AcctTransTests(TransactionTestCase):

    fixtures = ['pricing.json', 'trans_type.json']

    def setUp(self):
        self.password = PASSWORD
        self.today = timezone.now().date()
        self.yesterday = self.today - datetime.timedelta(days=1)

        # Hotel / Admin User
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.admin = create_hotel_user(hotel=self.hotel, group='hotel_admin')

        # Guest
        self.guest = make_guests(hotel=self.hotel, number=1)[0] #b/c returns a list
        # Messages
        self.messages = make_messages(
            hotel=self.hotel,
            user=self.admin,
            guest=self.guest
        )

        # TransTypes
        self.init_amt = TransType.objects.get(name='init_amt')
        self.recharge_amt = TransType.objects.get(name='recharge_amt')
        self.sms_used = TransType.objects.get(name='sms_used')
        self.phone_number_charge = TransType.objects.get(name='phone_number')
        # AcctStmt
        self.acct_stmts = create_acct_stmts(hotel=self.hotel)
        self.acct_stmt = self.acct_stmts[0]
        # AcctCost
        self.acct_cost, created = AcctCost.objects.get_or_create(hotel=self.hotel)
        # AcctTrans
        self.acct_trans = create_acct_trans(hotel=self.hotel)
        self.acct_tran = self.acct_trans[0]

        # Hotel 2 - use to make sure "AcctTrans.balance" and other 
        # methods don't conflict
        self.hotel_2 = create_hotel()
        self.acct_trans_2 = create_acct_trans(hotel=self.hotel_2)

    ### CREATE TESTS

    def test_create(self):
        # Guest
        self.assertEqual(Guest.objects.count(), 1)
        self.assertEqual(self.guest.hotel, self.hotel)
        # 10 Messages sent yesterday
        self.assertEqual(Message.objects.count(), 10)
        self.assertEqual(
            Message.objects.filter(hotel=self.hotel, insert_date=self.yesterday).count(),
            Message.objects.count()
        )

    ### MANAGER TESTS

    def test_trans_types(self):
        self.assertIsInstance(AcctTrans.objects.trans_types, TransTypeCache)

    ### Charges

    # 1. init_amt

    def test_init_amt(self):
        acct_tran, created = AcctTrans.objects.get_or_create(
            hotel=self.hotel,
            trans_type=self.init_amt
        )
        self.assertEqual(acct_tran.trans_type, self.init_amt)
        self.assertEqual(acct_tran.amount, self.acct_cost.init_amt)
        self.assertEqual(acct_tran.balance, self.acct_cost.init_amt)
        self.assertEqual(acct_tran.sms_used, 0)

    # 2. recharge_amt

    def test_recharge_amt(self):
        acct_tran, created = AcctTrans.objects.get_or_create(
            hotel=self.hotel,
            trans_type=self.recharge_amt
        )
        self.assertEqual(acct_tran.trans_type, self.recharge_amt)
        self.assertEqual(acct_tran.amount, self.acct_cost.recharge_amt)
        self.assertEqual(acct_tran.sms_used, 0)

    def test_rechare_amt_after_sms_used_that_balance_gets_calculated(self):
        # signup
        init_acct_tran, created = AcctTrans.objects.get_or_create(hotel=self.hotel,
            trans_type=self.init_amt)
        # use sms
        amount = -200
        balance = AcctTrans.objects.balance(self.hotel)
        usage_acct_tran = AcctTrans.objects.create(hotel=self.hotel, trans_type=self.sms_used,
            amount=amount, sms_used=amount, balance=(balance+amount))

        recharge_acct_tran, created = AcctTrans.objects.get_or_create(hotel=self.hotel,
            trans_type=self.recharge_amt)
        self.assertEqual(recharge_acct_tran.trans_type, self.recharge_amt)
        self.assertEqual(recharge_acct_tran.amount, self.acct_cost.recharge_amt)
        self.assertEqual(
            recharge_acct_tran.balance,
            (usage_acct_tran.balance + recharge_acct_tran.amount)
        )

    # 3. sms_used

    # def test_sms_used_validate_insert_date(self):
    #     with self.assertRaises(ValidationError):
    #         AcctTrans.objects.sms_used_validate_insert_date(self.today)

    #     self.assertIsNone(AcctTrans.objects.sms_used_validate_insert_date(
    #         self.yesterday))

    # def test_sms_used_validate_single_date_record(self):
    #     # test for "yesterday" b/c `sms_used` can only be calculated
    #     # for completed days, so it is a final # of SMS sent
    #     for ea in AcctTrans.objects.filter(hotel=self.hotel, insert_date__gte=self.yesterday):
    #         ea.delete()

    #     self.assertIsNone(AcctTrans.objects.sms_used_validate_single_date_record(
    #         hotel=self.hotel, insert_date=self.yesterday))

    #     AcctTrans.objects.sms_used(hotel=self.hotel, insert_date=self.yesterday)

    def test_sms_used_daily_message_count(self):
        self.assertEqual(self.hotel.messages.filter(
            insert_date=self.yesterday).count(), 10)

    def test_sms_used_mtd(self):
        for ea in AcctTrans.objects.filter(hotel=self.hotel, trans_type=self.sms_used):
            ea.delete()

        self.assertEqual(AcctTrans.objects.sms_used_mtd(hotel=self.hotel,
            insert_date=self.yesterday), 0)

        AcctTrans.objects.sms_used(hotel=self.hotel, insert_date=self.yesterday)
        self.assertEqual(AcctTrans.objects.sms_used_mtd(hotel=self.hotel,
            insert_date=self.yesterday), 10)

    # def test_sms_used(self):
    #     for ea in AcctTrans.objects.filter(hotel=self.hotel, trans_type=self.sms_used):
    #         ea.delete()

    #     acct_tran = AcctTrans.objects.sms_used(hotel=self.hotel, insert_date=self.yesterday)
    #     self.assertEqual(acct_tran.trans_type, self.sms_used)

    #     with self.assertRaises(ValidationError):
    #         AcctTrans.objects.sms_used(hotel=self.hotel, insert_date=self.yesterday)

    # 4. phone_number

    def test_phone_number_charge(self):
        # set the ``desc`` as an arbitrary ph num string
        acct_tran = AcctTrans.objects.phone_number_charge(
            self.hotel,
            phone_number=settings.DEFAULT_TO_PH
        )
        self.assertIsInstance(acct_tran, AcctTrans)
        self.assertEqual(acct_tran.hotel, self.hotel)
        self.assertEqual(acct_tran.trans_type, self.phone_number_charge)
        self.assertEqual(acct_tran.amount, -settings.PHONE_NUMBER_MONTHLY_COST)
        self.assertEqual(acct_tran.sms_used, 0)

    # get_or_create - specific 'trans_type'

    def test_get_or_create_sms_used(self):
        [x.delete() for x in AcctTrans.objects.filter(hotel=self.hotel, trans_type=self.sms_used)]
        self.assertEqual(AcctTrans.objects.filter(hotel=self.hotel, trans_type=self.sms_used).count(), 0)
        # 10 messages from yesterday need to be logged
        insert_date = timezone.now().date() - datetime.timedelta(days=1)
        self.assertEqual(self.hotel.messages.filter(insert_date=insert_date).count(), 10)

        acct_tran, created = AcctTrans.objects.get_or_create_sms_used(hotel=self.hotel,
            date=insert_date)

        self.assertEqual(AcctTrans.objects.filter(hotel=self.hotel, trans_type=self.sms_used).count(), 1)

    ### OTHER MANAGER TESTS

    def test_recharge_success(self):
        # this will set the current 'balance' to 0, so a recharge() call will
        # trigger a 'recharge_amt' transaction
        balance = AcctTrans.objects.balance(self.hotel)
        AcctTrans.objects.create(
            hotel=self.hotel,
            amount= -balance,
            trans_type=self.sms_used
        )
        acct_tran = AcctTrans.objects.recharge(self.hotel)
        self.assertEqual(acct_tran.trans_type, self.recharge_amt)

    def test_recharge_fail(self):
        # TODO
        pass

    def test_amount_to_recharge(self):
        balance = -100
        amount_to_recharge = AcctTrans.objects.amount_to_recharge(self.hotel, balance)
        self.assertEqual(
            amount_to_recharge,
            self.hotel.acct_cost.recharge_amt - balance
        )

    def test_check_balance_ok(self):
        self.assertTrue(AcctTrans.objects.balance(self.hotel) > self.hotel.acct_cost.balance_min)
        self.assertIsNone(AcctTrans.objects.check_balance(self.hotel))

    def test_check_balance_recharge_triggered(self):
        # set 'balance = 0'
        balance = AcctTrans.objects.balance(self.hotel)
        AcctTrans.objects.create(
            hotel=self.hotel,
            amount= -balance,
            trans_type=self.sms_used
        )
        # Calling this method should not trigger a 'recharge()'
        pre_trans = AcctTrans.objects.filter(hotel=self.hotel, trans_type=self.recharge_amt).count()
        AcctTrans.objects.check_balance(self.hotel)
        post_trans = AcctTrans.objects.filter(hotel=self.hotel, trans_type=self.recharge_amt).count()
        self.assertEqual(pre_trans+1, post_trans)

    def test_check_balance_auto_recharge_off(self):
        # Twilio Subaccount
        # subaccount, _ = Subaccount.objects.get_or_create(self.hotel)
        # set 'balance = 0'
        balance = AcctTrans.objects.balance(self.hotel)
        AcctTrans.objects.create(
            hotel=self.hotel,
            amount= -balance,
            trans_type=self.sms_used
        )
        self.acct_cost.auto_recharge = False
        self.acct_cost.save()
        # triggering a 'recharge()' will now raise an error b/c 'auto_recharge' is OFF
        with self.assertRaises(AutoRechargeOffExcp):
            AcctTrans.objects.check_balance(self.hotel)
