from mock import patch

from django.test import TestCase
from django.conf import settings
from django.db.models import Sum

from model_mommy import mommy

from account.models import AcctTrans, AcctStmt, TransType, AcctCost, Pricing
from account.tasks import (create_initial_acct_trans_and_stmt, get_or_create_acct_stmt,
    charge_hotel_monthly_for_phone_numbers, eod_update_or_create_sms_used)
from account.tests.factory import create_acct_stmt, create_acct_tran
from main.models import Hotel
from main.tests.factory import create_hotel
from sms.tests.factory import create_phone_number
from utils.models import Dates
from utils.tests.runners import celery_set_eager


class CreateInitialAcctTransAndAcctStmtTests(TestCase):

    fixtures = ['trans_type.json']

    def setUp(self):
        self.hotel = create_hotel()
        self.pricing = mommy.make(Pricing, hotel=self.hotel)
        self.acct_cost = AcctCost.objects.get_or_create(hotel=self.hotel)
        self.init_amt = TransType.objects.get(name='init_amt')
        self.sms_used = TransType.objects.get(name='sms_used')
        # dates
        self.dates = Dates()
        self.today = self.dates._today

        celery_set_eager()

    def test_acct_trans(self):
        self.assertEqual(AcctTrans.objects.filter(hotel=self.hotel).count(), 0)

        create_initial_acct_trans_and_stmt.delay(self.hotel.id)

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

        create_initial_acct_trans_and_stmt.delay(self.hotel.id)

        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 1)

    def test_pricing(self):
        [x.delete() for x in Pricing.objects.filter(hotel=self.hotel)]
        self.assertEqual(Pricing.objects.filter(hotel=self.hotel).count(), 0)

        create_initial_acct_trans_and_stmt.delay(self.hotel.id)

        self.assertEqual(Pricing.objects.filter(hotel=self.hotel).count(), 1)

    def test_get_or_create_acct_stmt(self):
        dates = Dates()
        today = dates._today
        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 0)

        init_acct_stmt = create_acct_stmt(self.hotel, year=today.year, month=today.month)
        get_or_create_acct_stmt.delay(self.hotel.id, year=today.year, month=today.month)

        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 1)
        acct_stmt = AcctStmt.objects.filter(hotel=self.hotel)[0]
        self.assertIsInstance(acct_stmt, AcctStmt)
        self.assertEqual(acct_stmt, init_acct_stmt)
        self.assertTrue(acct_stmt.modified > init_acct_stmt.modified)

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

            charge_hotel_monthly_for_phone_numbers.delay(self.hotel.id)

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
            charge_hotel_monthly_for_phone_numbers.delay(self.hotel.id)

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

    def test_eod_update_or_create_sms_used(self):
        init_acct_tran = create_acct_tran(self.hotel, self.sms_used, self.today)

        eod_update_or_create_sms_used.delay()

        post_acct_tran = AcctTrans.objects.filter(hotel=self.hotel,
            trans_type=self.sms_used).order_by('-modified').first()

        self.assertTrue(post_acct_tran.modified > init_acct_tran.modified)
