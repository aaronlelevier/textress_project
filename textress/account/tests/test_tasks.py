from django.test import TestCase

from account.models import AcctTrans, AcctStmt, TransType, AcctCost
from account.tasks import create_initial_acct_trans_and_stmt
from main.models import Hotel
from main.tests.factory import create_hotel
from utils.tests.runners import celery_set_eager


class CreateInitialAcctTransAndAcctStmtTests(TestCase):

    fixtures = ['trans_type.json']

    def setUp(self):
        self.hotel = create_hotel()
        self.acct_cost = AcctCost.objects.get_or_create(hotel=self.hotel)
        self.init_amt_type = TransType.objects.get(name='init_amt')

        celery_set_eager()

    def test_acct_trans(self):
        self.assertEqual(AcctTrans.objects.filter(hotel=self.hotel).count(), 0)

        create_initial_acct_trans_and_stmt.delay(self.hotel.id)

        self.assertEqual(AcctTrans.objects.filter(hotel=self.hotel).count(), 1)
        acct_tran = AcctTrans.objects.first()
        self.assertEqual(acct_tran.trans_type, self.init_amt_type)

    def test_acct_stmt(self):
        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 0)

        create_initial_acct_trans_and_stmt.delay(self.hotel.id)

        self.assertEqual(AcctStmt.objects.filter(hotel=self.hotel).count(), 1)
