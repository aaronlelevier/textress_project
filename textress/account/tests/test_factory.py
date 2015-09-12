from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from account.models import (
    AcctStmt, TransType, AcctTrans, CHARGE_AMOUNTS, BALANCE_AMOUNTS,
    TRANS_TYPES
    )
from account.tests import factory
from main.tests.factory import create_hotel


class FactoryTests(TransactionTestCase):

    def setUp(self):
        self.hotel = create_hotel()

    def test_randint(self):
        i = factory._randint()
        self.assertIsInstance(i, int)

    def test_create_trans_type(self):
        tt = factory.create_trans_type(TRANS_TYPES[0][0])
        self.assertIsInstance(tt, TransType)

    def test_create_trans_type_invalid(self):
        with self.assertRaises(Exception):
            factory.create_trans_type(name='invalid_trans_type')

    def test_create_trans_types(self):
        tt = factory.create_trans_types()
        self.assertEqual(len(TRANS_TYPES), TransType.objects.count())

    def test_create_acct_stmt(self):
        now = timezone.now()
        stmt = factory.create_acct_stmt(
            hotel=self.hotel,
            year=now.year,
            month=now.month
            )
        self.assertIsInstance(stmt, AcctStmt)
        self.assertEqual(AcctStmt.objects.count(), 1)

    def test_create_acct_stmts(self):
        factory.create_acct_stmts(self.hotel)
        self.assertEqual(AcctStmt.objects.count(), 12)

    def test_create_account_tran(self):
        trans_types = factory.create_trans_types()
        at = factory.create_acct_tran(
            hotel=self.hotel,
            trans_type=trans_types[0],
            insert_date=timezone.now()
            )
        self.assertIsInstance(at, AcctTrans)

    def test_create_acct_trans(self):
        self.assertEqual(AcctTrans.objects.count(), 0)
        acct_trans = factory.create_acct_trans(self.hotel)
        self.assertTrue(AcctTrans.objects.count() > 10)