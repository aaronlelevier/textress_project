import datetime
from mock import patch

from django.test import TestCase
from django.conf import settings
from django.db.models import Sum

from model_mommy import mommy

from account import tasks
from account.models import AcctTrans, AcctStmt, TransType, AcctCost, Pricing
from account.tests.factory import create_acct_stmt, create_acct_tran
from main.models import Hotel
from main.tests.factory import create_hotel
from sms.tests.factory import create_phone_number
from utils.models import Dates
from utils.tests.runners import celery_set_eager


class CreateInitialAcctTransAndAcctStmtTests(TestCase):

    fixtures = ['trans_type.json']

    def setUp(self):
        # Hotel 1
        self.hotel = create_hotel()
        self.pricing = mommy.make(Pricing, hotel=self.hotel)
        self.acct_cost = AcctCost.objects.get_or_create(hotel=self.hotel)
        # Hotel 2
        self.hotel2 = create_hotel()
        self.pricing2 = mommy.make(Pricing, hotel=self.hotel2)
        self.acct_cost2 = AcctCost.objects.get_or_create(hotel=self.hotel2)
        # TransType
        self.init_amt = TransType.objects.get(name='init_amt')
        self.sms_used = TransType.objects.get(name='sms_used')
        # dates
        self.dates = Dates()
        self.today = self.dates._today

        celery_set_eager()

    # create_initial_acct_trans_and_stmt

    def test_acct_trans(self):
        self.assertEqual(AcctTrans.objects.filter(hotel=self.hotel).count(), 0)

        tasks.create_initial_acct_trans_and_stmt.delay(self.hotel.id)

        # 2 Acct Trans b/c an SMS used will always be calculated for "day-of"
        # AcctTrans when calling ``AcctStmt.objects.get_or_create`` because this
        # is needed to get the current balance.
        self.assertEqual(AcctTrans.objects.filter(hotel=self.hotel).count(), 2)
        acct_tran_init_amt = AcctTrans.objects.filter(trans_type=self.init_amt).exists()
        self.assertTrue(acct_tran_init_amt)
        acct_tran_sms_used = AcctTrans.objects.filter(trans_type__name='sms_used').exists()
        self.assertTrue(acct_tran_sms_used)

    def test_acct_stmt(self):
        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 0)

        tasks.create_initial_acct_trans_and_stmt.delay(self.hotel.id)

        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 1)

    def test_pricing(self):
        [x.delete() for x in Pricing.objects.filter(hotel=self.hotel)]
        self.assertEqual(Pricing.objects.filter(hotel=self.hotel).count(), 0)

        tasks.create_initial_acct_trans_and_stmt.delay(self.hotel.id)

        self.assertEqual(Pricing.objects.filter(hotel=self.hotel).count(), 1)

    # get_or_create_acct_stmt

    def test_get_or_create_acct_stmt(self):
        dates = Dates()
        today = dates._today
        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 0)
        init_acct_stmt = create_acct_stmt(self.hotel, year=today.year, month=today.month)

        tasks.get_or_create_acct_stmt.delay(self.hotel.id, year=today.year, month=today.month)

        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 1)
        acct_stmt = AcctStmt.objects.filter(hotel=self.hotel)[0]
        self.assertIsInstance(acct_stmt, AcctStmt)
        self.assertEqual(acct_stmt, init_acct_stmt)
        self.assertTrue(acct_stmt.modified > init_acct_stmt.modified)

    # get_or_create_acct_stmt_all_hotels

    def test_get_or_create_acct_stmt_all_hotels(self):
        dates = Dates()
        today = dates._today
        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 0)
        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel2).count(), 0)

        tasks.get_or_create_acct_stmt_all_hotels.delay(year=today.year, month=today.month)

        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 1)
        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel2).count(), 1)

    # acct_stmt_update_prev

    def test_first_of_month(self):
        self.assertEqual(tasks.FIRST_OF_MONTH, Dates().first_of_month())

    def test_first_of_month(self):
        tasks.FIRST_OF_MONTH = Dates()._today

        self.assertNotEqual(tasks.FIRST_OF_MONTH, Dates().first_of_month())

    def test_acct_stmt_update_prev__create(self):
        """
        Acts as if for "next month", so the "acct stmt prev" that get's 
        generated will be for this month. Have to do this way b/c can't 
        create Hotel in past.
        """
        [x.delete() for x in AcctStmt.objects.filter(hotel=self.hotel)]
        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 0)
        first_of_next_month = Dates().first_of_next_month()

        tasks.acct_stmt_update_prev.delay(hotel_id=self.hotel.id, first_of_month=first_of_next_month)

        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 1)
        acct_stmt = AcctStmt.objects.get(hotel=self.hotel)
        self.assertEqual(acct_stmt.month, self.today.month)
        self.assertEqual(acct_stmt.year, self.today.year)

    def test_acct_stmt_update_prev__update(self):
        [x.delete() for x in AcctStmt.objects.filter(hotel=self.hotel)]
        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 0)
        first_of_next_month = Dates().first_of_next_month()

        tasks.acct_stmt_update_prev.delay(hotel_id=self.hotel.id, first_of_month=first_of_next_month)
        first_acct_stmt = AcctStmt.objects.first()
        tasks.acct_stmt_update_prev.delay(hotel_id=self.hotel.id, first_of_month=first_of_next_month)
        second_acct_stmt = AcctStmt.objects.first()

        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 1)
        self.assertEqual(first_acct_stmt.month, self.today.month)
        self.assertEqual(first_acct_stmt.year, self.today.year)
        self.assertEqual(first_acct_stmt.created, second_acct_stmt.created)
        self.assertTrue(first_acct_stmt.modified < second_acct_stmt.modified)

    def test_acct_stmt_update_prev__dont_create(self):
        """
        Hotel wasn't here last month, so don't need to create a 
        "acct stmt prev"
        """
        [x.delete() for x in AcctStmt.objects.filter(hotel=self.hotel)]
        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 0)
        last_month_end = Dates().last_month_end()

        tasks.acct_stmt_update_prev.delay(hotel_id=self.hotel.id, first_of_month=last_month_end)

        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 0)

    def test_acct_stmt_update_prev__dont_update(self):
        date = Dates().last_month_end()
        acct_stmt, created = AcctStmt.objects.get_or_create(hotel=self.hotel,
            month=date.month, year=date.year)
        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 1)
        first_acct_stmt = AcctStmt.objects.first()

        tasks.acct_stmt_update_prev.delay(hotel_id=self.hotel.id)
        second_acct_stmt = AcctStmt.objects.first()

        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 1)
        self.assertEqual(first_acct_stmt.created, second_acct_stmt.created)
        self.assertEqual(first_acct_stmt.modified, second_acct_stmt.modified)

    # acct_stmt_update_prev_all_hotels

    def test_acct_stmt_update_prev_all_hotels(self):
        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 0)
        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel2).count(), 0)
        first_of_next_month = Dates().first_of_next_month()

        tasks.acct_stmt_update_prev_all_hotels.delay(first_of_month=first_of_next_month)

        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 1)
        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel2).count(), 1)

    # charge_hotel_monthly_for_phone_numbers

    def test_charge_hotel_monthly_for_phone_numbers(self):
        dates = Dates()
        today = dates._today

        with self.settings(PHONE_NUMBER_MONTHLY_CHARGE_DAY=today.day):
            self.assertEqual(AcctTrans.objects.filter(
                hotel=self.hotel,
                trans_type__name='phone_number',
                insert_date__day=settings.PHONE_NUMBER_MONTHLY_CHARGE_DAY).count(), 0)

            ph = create_phone_number(self.hotel)
            ph2 = create_phone_number(self.hotel)
            self.assertEqual(self.hotel.phone_numbers.count(), 2)

            tasks.charge_hotel_monthly_for_phone_numbers.delay(self.hotel.id)

            ph_num_acct_trans = AcctTrans.objects.filter(
                hotel=self.hotel,
                trans_type__name='phone_number',
                insert_date__day=settings.PHONE_NUMBER_MONTHLY_CHARGE_DAY
            )
            self.assertEqual(ph_num_acct_trans.count(), 2)
            self.assertEqual(
                ph_num_acct_trans.aggregate(Sum('amount'))['amount__sum'],
                2 * -(settings.PHONE_NUMBER_MONTHLY_COST)
            )

            # re-running by accident won't recharge them b/c filtering out already 
            # charged "phone_numbers"
            tasks.charge_hotel_monthly_for_phone_numbers.delay(self.hotel.id)

            ph_num_acct_trans = AcctTrans.objects.filter(
                hotel=self.hotel,
                trans_type__name='phone_number',
                insert_date__day=settings.PHONE_NUMBER_MONTHLY_CHARGE_DAY
            )
            self.assertEqual(ph_num_acct_trans.count(), 2)
            self.assertEqual(
                ph_num_acct_trans.aggregate(Sum('amount'))['amount__sum'],
                2 * -(settings.PHONE_NUMBER_MONTHLY_COST)
            )

    def test_charge_hotel_monthly_for_phone_numbers__run_on_random_day(self):
        """
        If 'today.day' is not the CHARGE_DAY then the Hotel shouldn't be charged 
        the 'monthly phone number charge'.
        """
        dates = Dates()
        today = dates._today.day
        not_today = today+1

        # charge day is "not today", so nothing should happen
        with self.settings(PHONE_NUMBER_MONTHLY_CHARGE_DAY=not_today):
            self.assertEqual(AcctTrans.objects.filter(
                hotel=self.hotel,
                trans_type__name='phone_number',
                insert_date__day=today).count(), 0)

            ph = create_phone_number(self.hotel)
            self.assertEqual(self.hotel.phone_numbers.count(), 1)

            tasks.charge_hotel_monthly_for_phone_numbers.delay(self.hotel.id)

            self.assertEqual(AcctTrans.objects.filter(
                hotel=self.hotel,
                trans_type__name='phone_number',
                insert_date__day=today).count(), 0)

    # charge_hotel_monthly_for_phone_numbers_all_hotels

    def test_charge_hotel_monthly_for_phone_numbers_all_hotels(self):
        dates = Dates()
        today = dates._today

        with self.settings(PHONE_NUMBER_MONTHLY_CHARGE_DAY=today.day):
            self.assertEqual(AcctTrans.objects.filter(
                hotel=self.hotel,
                trans_type__name='phone_number',
                insert_date__day=settings.PHONE_NUMBER_MONTHLY_CHARGE_DAY).count(), 0)
            self.assertEqual(AcctTrans.objects.filter(
                hotel=self.hotel2,
                trans_type__name='phone_number',
                insert_date__day=settings.PHONE_NUMBER_MONTHLY_CHARGE_DAY).count(), 0)

            ph = create_phone_number(self.hotel)
            ph2 = create_phone_number(self.hotel2)
            self.assertEqual(self.hotel.phone_numbers.count(), 1)
            self.assertEqual(self.hotel2.phone_numbers.count(), 1)

            tasks.charge_hotel_monthly_for_phone_numbers_all_hotels.delay()

            self.assertEqual(
                AcctTrans.objects.filter(
                    hotel=self.hotel,
                    trans_type__name='phone_number',
                    insert_date__day=settings.PHONE_NUMBER_MONTHLY_CHARGE_DAY).count(), 1)
            self.assertEqual(
                AcctTrans.objects.filter(
                    hotel=self.hotel2,
                    trans_type__name='phone_number',
                    insert_date__day=settings.PHONE_NUMBER_MONTHLY_CHARGE_DAY).count(), 1)

            # If ran again, won't re-charge the Hotel(s) for their monthly 
            # PhoneNumber b/c already charged them for the month

            tasks.charge_hotel_monthly_for_phone_numbers_all_hotels.delay()

            self.assertEqual(
                AcctTrans.objects.filter(
                    hotel=self.hotel,
                    trans_type__name='phone_number',
                    insert_date__day=settings.PHONE_NUMBER_MONTHLY_CHARGE_DAY).count(), 1)
            self.assertEqual(
                AcctTrans.objects.filter(
                    hotel=self.hotel2,
                    trans_type__name='phone_number',
                    insert_date__day=settings.PHONE_NUMBER_MONTHLY_CHARGE_DAY).count(), 1)

    # eod_update_or_create_sms_used

    def test_eod_update_or_create_sms_used(self):
        init_acct_tran = create_acct_tran(self.hotel, self.sms_used, self.today)

        tasks.eod_update_or_create_sms_used.delay()

        post_acct_tran = AcctTrans.objects.filter(hotel=self.hotel,
            trans_type=self.sms_used).order_by('-modified').first()
        self.assertTrue(post_acct_tran.modified > init_acct_tran.modified)
