import datetime
import pytz

from django.db.models import Max, Sum
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.utils import timezone

from model_mommy import mommy

from account.models import (Dates, Pricing, TransType, AcctCost, AcctStmt, AcctTrans,
    CHARGE_AMOUNTS, BALANCE_AMOUNTS)
from account.tests.factory import create_acct_stmts, create_acct_trans
from concierge.tests.factory import make_guests, make_messages
from main.tests.factory import create_hotel, create_hotel_user, PASSWORD
from utils import create


class DatesTests(TestCase):

    def setUp(self):
        self.tzinfo = pytz.timezone(settings.TIME_ZONE)

    def test_tzinfo(self):
        dates = Dates()
        self.assertTrue(hasattr(dates, 'tzinfo'))

    def test_all_dates(self):
        dates = Dates()
        now = timezone.now()

        self.assertTrue(dates._now)
        self.assertEqual(dates._today, now.date())
        self.assertEqual(dates._year, now.year)
        self.assertEqual(dates._month, now.month)

    def test_first_of_month(self):
        dates = Dates()
        first_of_month = dates.first_of_month(month=1, year=1)
        self.assertEqual(
            first_of_month,
            datetime.datetime(day=1, month=1, year=1, tzinfo=self.tzinfo)
        )

    def test_first_of_month_defaul(self):
        dates = Dates()
        first_of_month = dates.first_of_month()
        self.assertEqual(
            first_of_month,
            datetime.datetime(day=1, month=dates._today.month,
                year=dates._today.year, tzinfo=self.tzinfo)
        )


class AbstractBaseTests(TestCase):

    def test_AbstractBase_properties(self):
        # auto fields work
        price = mommy.make(Pricing)
        assert isinstance(price.created, datetime.datetime)
        assert isinstance(price.modified, datetime.datetime)


class PricingTests(TestCase):
    # NOTE: Am skipping testing save() b/c these are static Pricing Tiers
    #   that are created once and hardly ever changed.

    fixtures = ['pricing.json']

    def test_fixtures(self):
        free_price = Pricing.objects.get(tier_name="Free")
        assert isinstance(free_price, Pricing)

    def test_get_cost(self):
        assert Pricing.objects.get_cost(units=200, units_prev=0) == 0

    def test_get_cost_two_tiers(self):
        units = 300
        tier = Pricing.objects.get(start__lte=units, end__gte=units)
        print((units - (tier.start-1)) * tier.price)
        print(Pricing.objects.get_cost(units=units, units_prev=0))
        assert (units - (tier.start-1)) * tier.price == Pricing.objects.get_cost(units=units, units_prev=0)

    def test_get_cost_three_tiers(self):
        units = 2300
        cost = 100*0.0525 + 2000*0.0550
        tier = Pricing.objects.get(start__lte=units, end__gte=units)
        print(cost)
        print(Pricing.objects.get_cost(units=units, units_prev=0))
        assert cost == Pricing.objects.get_cost(units=units, units_prev=0)


class TransTypeTests(TestCase):
    # Test contains all TransTypes
    # This Model is also static and does not change.

    fixtures = ['trans_type.json']

    def test_types(self):
        init_amt = TransType.objects.get(name='init_amt')
        recharge_amt = TransType.objects.get(name='recharge_amt')
        sms_used = TransType.objects.get(name='sms_used')
        bulk_discount = TransType.objects.get(name='bulk_discount')

        self.assertIsInstance(init_amt, TransType)
        self.assertEqual(str(init_amt), init_amt.name)
        self.assertEqual(len(TransType.objects.all()), 4)


class AcctCostTests(TestCase):
    '''
    Hotel can only have 1 AcctCost record. Can be updated.
    '''

    def setUp(self):
        self.password = PASSWORD
        self.hotel = create_hotel()

    def test_create(self):
        # Dave starts with the "Default Amounts" when creating his ``AcctCost``
        acct_cost, created = AcctCost.objects.get_or_create(hotel=self.hotel)
        self.assertTrue(created)
        self.assertIsInstance(acct_cost, AcctCost)
        self.assertEqual(acct_cost.init_amt, CHARGE_AMOUNTS[0][0])
        self.assertEqual(acct_cost.balance_min, BALANCE_AMOUNTS[0][0])
        self.assertEqual(acct_cost.recharge_amt, CHARGE_AMOUNTS[0][0])


        # create new actually modifies original b/c p/ Hotel, singleton obj
        new_acct_cost, created = AcctCost.objects.get_or_create(
            hotel=self.hotel,
            balance_min=BALANCE_AMOUNTS[2][0],
            recharge_amt=CHARGE_AMOUNTS[2][0]
            )
        self.assertFalse(created)
        assert acct_cost == new_acct_cost
        assert len(AcctCost.objects.all()) == 1
        assert new_acct_cost.balance_min == BALANCE_AMOUNTS[2][0]
        assert new_acct_cost.recharge_amt == CHARGE_AMOUNTS[2][0]


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

    def test_get_absolute_url(self):
        assert (self.acct_stmt.get_absolute_url() ==
                reverse('acct_stmt_detail',
                    kwargs={'year':self.acct_stmt.year, 'month':self.acct_stmt.month}
                    )
                )

    ### MANAGER TESTS ###

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

    # def test_get_or_create_previous_month(self):
        
    #     acct_stmt, created = AcctStmt.objects.get_or_create(
    #         hotel=self.hotel,
    #         month=self.today.month,
    #         year=self.today.year
    #         )
    #     self.assertIsInstance(acct_stmt, AcctStmt)
    #     self.assertTrue(created)

    def test_acct_trans_balance(self):
        acct_stmt, created = AcctStmt.objects.get_or_create(
            hotel=self.hotel,
            month=self.today.month,
            year=self.today.year
            )

        total_sms = acct_stmt.total_sms
        assert total_sms

        # Send 1 message, and "total_sms" for AcctStmt will change,
        # But, "balance" will not unless triggering a re-fill
        make_messages(hotel=self.hotel, user=self.admin, guest=self.guest, number=1)
        acct_stmt, created = AcctStmt.objects.get_or_create(
            hotel=self.hotel,
            month=self.today.month,
            year=self.today.year
            )
        new_total_sms = acct_stmt.total_sms
        assert new_total_sms
        assert new_total_sms > total_sms


class AcctStmtNewHotelTests(TestCase):
    # Test Hotels that have only signed up, and don't have 
    # any SMS sent yet

    # Contains all TransTypes
    fixtures = ['trans_type.json']

    def setUp(self):
        self.password = PASSWORD
        self.today = timezone.now().date()
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, 'admin')

    def test_sms_used_prev(self):
        self.assertEqual(AcctTrans.objects.sms_used_prev(self.hotel), 0)


class AcctTransTests(TestCase):

    # Contains all TransTypes
    fixtures = ['trans_type.json']

    def setUp(self):
        self.password = '1234'
        self.today = timezone.now().date()

        # Hotel
        self.hotel = create_hotel()

        # create "Hotel Manager" Group
        create._get_groups_and_perms()

        # Admin
        self.admin = mommy.make(User, username='admin')
        self.admin.groups.add(Group.objects.get(name="hotel_admin"))
        self.admin.set_password(self.password)
        self.admin.save()
        self.admin.profile.update_hotel(hotel=self.hotel)
        # Hotel Admin ID
        self.hotel.admin_id = self.admin.id
        self.hotel.save()

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
        self.bulk_discount = TransType.objects.get(name='bulk_discount')

        # AcctStmt
        self.acct_stmts = create_acct_stmts(hotel=self.hotel)
        self.acct_stmt = self.acct_stmts[0]

        # AcctCost
        self.acct_cost, created = AcctCost.objects.get_or_create(hotel=self.hotel)

        # AcctTrans
        self.acct_trans = create_acct_trans(hotel=self.hotel)
        self.acct_tran = self.acct_trans[0]

    ### CREATE TESTS ###

    def test_create_acct_cost(self):
        assert self.acct_cost.recharge_amt

    ### MANAGER TESTS ###

    def test_monthly_trans(self):
        monthly_trans = AcctTrans.objects.filter(
            hotel=self.hotel, 
            insert_date__month=self.today.month,
            insert_date__year=self.today.year
            )
        monthly_trans_mgr = AcctTrans.objects.monthly_trans(
            hotel=self.hotel
            )
        assert len(monthly_trans) == len(monthly_trans_mgr)

    def test_previous_monthly_trans(self):
        first_of_month = datetime.date(self.today.year, self.today.month, 1)
        trans = AcctTrans.objects.filter(hotel=self.hotel, insert_date__lt=first_of_month)
        trans_mgr = AcctTrans.objects.previous_monthly_trans(
            hotel=self.hotel,
            month=self.today.month,
            year=self.today.year
            )
        assert len(trans) == len(trans_mgr)

    def test_balance(self):
        assert (AcctTrans.objects.balance() ==
                AcctTrans.objects.aggregate(Sum('amount'))['amount__sum'])

    def test_init_amt_mgr(self):
        acct_cost = AcctCost.objects.get(hotel=self.hotel)
        acct_tran, created = AcctTrans.objects.get_or_create(
            hotel=self.hotel, trans_type=self.init_amt)
        assert acct_cost.init_amt == acct_tran.amount

    def test_recharge_amt_mgr(self):
        acct_cost = AcctCost.objects.get(hotel=self.hotel)
        acct_tran, created = AcctTrans.objects.get_or_create(
            hotel=self.hotel, trans_type=self.recharge_amt)
        assert acct_cost.recharge_amt == acct_tran.amount

    def test_sms_used_mgr(self):
        acct_cost = AcctCost.objects.get(hotel=self.hotel)
        acct_tran, created = AcctTrans.objects.get_or_create(
            hotel=self.hotel, trans_type=self.recharge_amt)
        assert acct_cost.recharge_amt == acct_tran.amount

    def test_sms_used_max_date(self):
        max_date = (AcctTrans.objects.filter(trans_type=self.sms_used)
                                     .aggregate(Max('insert_date'))['insert_date__max'])
        max_date_mgr = AcctTrans.objects.sms_used_max_date()
        assert max_date == max_date_mgr

    def test_sms_used_on_date(self):
        max_date = AcctTrans.objects.sms_used_max_date()
        assert AcctTrans.objects.sms_used_on_date(date=max_date)

    def test_phone_number_charge(self):
        # set the ``desc`` as an arbitrary ph num string
        acct_tran = AcctTrans.objects.phone_number_charge(self.hotel,
            desc=settings.DEFAULT_TO_PH)
        self.assertIsInstance(acct_tran, AcctTrans)
        self.assertEqual(acct_tran.amount, -settings.PHONE_NUMBER_MONTHLY_COST)

    def test_recharge(self):
        # ``recharge()`` returns None if it is not triggered
        old_balance = AcctTrans.objects.filter(hotel=self.hotel).balance()
        print('old_balance:', old_balance)
        recharge_amt, created = AcctTrans.objects.recharge(self.hotel, old_balance)
        self.assertIsNone(recharge_amt)

        # Create a fake charge to cause a call to ``.recharge()``
        AcctTrans.objects.phone_number_charge(hotel=self.hotel, desc=settings.DEFAULT_TO_PH)
        AcctTrans.objects.phone_number_charge(hotel=self.hotel, desc=settings.DEFAULT_TO_PH)
        AcctTrans.objects.phone_number_charge(hotel=self.hotel, desc=settings.DEFAULT_TO_PH)
        AcctTrans.objects.phone_number_charge(hotel=self.hotel, desc=settings.DEFAULT_TO_PH)

        # the balance of credits is higher than the acct_cost.balance_min, so no recharge occurs
        # set balance=0 b/c min balance is 100, so this will trigger a recharge
        current_balance = AcctTrans.objects.filter(hotel=self.hotel).balance()
        print "current_balance:", current_balance
        recharge_amt, created = AcctTrans.objects.recharge(self.hotel, balance=current_balance)
        print('recharge w/ balance=0:', recharge_amt.amount)
        assert recharge_amt.amount
        assert recharge_amt
        assert recharge_amt.trans_type == self.recharge_amt

        new_balance = AcctTrans.objects.filter(hotel=self.hotel).balance()

        print('self.hotel.acct_cost.recharge_amt:', self.hotel.acct_cost.recharge_amt)
        print('recharge_amt.amount:', recharge_amt.amount)
        print('old_balance:', old_balance, 'new_balance:', new_balance)
        print('balance_min:', self.hotel.acct_cost.balance_min)
        print('new_balance:', new_balance)
        self.assertTrue(new_balance >= self.hotel.acct_cost.balance_min)

    # def test_sms_used_mgr_no_messages(self):
    #     # Remove all Messages for today, so shouldn't be creating a `sms_used` AcctTrans record
    #     messages = self.hotel.messages.filter(insert_date=self.today)
    #     for m in messages:
    #         m.delete()

    #     acct_tran, created = AcctTrans.objects.sms_used(hotel=self.hotel,
    #         trans_type=self.sms_used)
    #     assert not acct_tran
    #     assert not created

    # def test_sms_used_mgr_messages_get(self):
    #     # Create initial messages for today and `sms_used` AcctTrans record
    #     messages = make_messages(
    #         hotel=self.hotel,
    #         user=self.admin,
    #         guest=self.guest
    #         )
    #     acct_tran, created = AcctTrans.objects.sms_used(hotel=self.hotel,
    #         trans_type=self.sms_used)

    #     # More messages should be an AcctTrans `sms_used` get(), not create()
    #     messages = make_messages(
    #         hotel=self.hotel,
    #         user=self.admin,
    #         guest=self.guest
    #         )
    #     acct_tran, created = AcctTrans.objects.sms_used(hotel=self.hotel,
    #         trans_type=self.sms_used)
    #     assert acct_tran
    #     assert not created

    # def test_sms_used_mgr_messages_create(self):
    #     # Create `sms_used` AcctTrans record for the day

    #     # Prep by deleting all `sms_used` AcctTrans for the day
    #     acct_trans = AcctTrans.objects.filter(hotel=self.hotel,
    #         trans_type=self.sms_used, insert_date=self.today)
    #     for ac in acct_trans:
    #         ac.delete()

    #     # Populate messages, and assure AcctTrans.sms_used() populates a create() record
    #     messages = make_messages(
    #         hotel=self.hotel,
    #         user=self.admin,
    #         guest=self.guest
    #         )
    #     acct_tran, created = AcctTrans.objects.sms_used(hotel=self.hotel,
    #         trans_type=self.sms_used)
    #     assert acct_tran
    #     assert created

    def test_balance_field(self):
        at = AcctTrans.objects.last()
        self.assertTrue(at.balance)