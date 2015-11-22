from django.test import TestCase

from model_mommy import mommy

from account.models import AcctTrans, AcctStmt, TransType, AcctCost, Pricing
from account.tasks import create_initial_acct_trans_and_stmt, get_or_create_acct_stmt
from account.tests.factory import create_acct_stmt
from main.models import Hotel
from main.tests.factory import create_hotel
from utils.models import Dates
from utils.tests.runners import celery_set_eager


class CreateInitialAcctTransAndAcctStmtTests(TestCase):

    fixtures = ['trans_type.json']

    def setUp(self):
        self.hotel = create_hotel()
        self.pricing = mommy.make(Pricing, hotel=self.hotel)
        self.acct_cost = AcctCost.objects.get_or_create(hotel=self.hotel)
        self.init_amt = TransType.objects.get(name='init_amt')

        celery_set_eager()

    def test_acct_trans(self):
        self.assertEqual(AcctTrans.objects.filter(hotel=self.hotel).count(), 0)

        create_initial_acct_trans_and_stmt.delay(self.hotel.id)

        # 2 Acct Trans b/c an SMS used will always be calculated for "day-of"
        # AcctTrans when calling ``AcctStmt.objects.get_or_create`` because this
        # is needed to get the current blance.
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
        init_acct_stmt = create_acct_stmt(self.hotel, year=today.year, month=today.month)

        acct_stmt, created = get_or_create_acct_stmt(self.hotel.id, year=today.year, month=today.month)

        self.assertIsInstance(acct_stmt, AcctStmt)
        self.assertFalse(created)
        self.assertEqual(acct_stmt, init_acct_stmt)
        self.assertTrue(acct_stmt.modified > init_acct_stmt.modified)
