from django.test import TestCase
from django.utils import timezone

from account.models import (
    AcctStmt, TransType, AcctTrans, CHARGE_AMOUNTS, BALANCE_AMOUNTS,
    TRANS_TYPES
    )
from account.tests import factory
from main.models import Hotel
from main.tests.factory import create_hotel


class FactoryTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()

    def test_randint(self):
        i = factory._randint()
        self.assertIsInstance(i, int)

    def test_create_trans_types(self):
        tt = factory.make_trans_types()
        self.assertEqual(len(TRANS_TYPES), TransType.objects.count())

    def test_acct_stmt(self):
        now = timezone.now()
        stmt = factory._acct_stmt(
            hotel=self.hotel,
            year=now.year,
            month=now.month
            )
        self.assertIsInstance(stmt, AcctStmt)
        self.assertEqual(AcctStmt.objects.count(), 1)

    def test_make_acct_stmts(self):
        factory.make_acct_stmts(self.hotel)
        self.assertEqual(AcctStmt.objects.count(), 12)

    def test_acct_trans(self):
        trans_types = factory.make_trans_types()
        at = factory._acct_trans(
            hotel=self.hotel,
            trans_type=trans_types[0],
            insert_date=timezone.now()
            )
        self.assertIsInstance(at, AcctTrans)

    def test_make_acct_trans(self):
        self.assertEqual(AcctTrans.objects.count(), 0)
        acct_trans = factory.make_acct_trans(self.hotel)
        self.assertTrue(AcctTrans.objects.count() > 10) # roughly 30 test fixtures made for a month




