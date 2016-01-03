from django.conf import settings
from django.test import TestCase, TransactionTestCase
from django.utils import timezone

from account.models import (
    AcctStmt, TransType, AcctTrans, CHARGE_AMOUNTS, BALANCE_AMOUNTS,
    TRANS_TYPES
    )
from account.tests import factory
from main.tests.factory import create_hotel


class FactoryTests(TestCase):

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
        now = timezone.localtime(timezone.now())
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

    # create_account_tran

    def test_create_account_tran__recharge_amt(self):
        trans_types = factory.create_trans_types()
        trans_type = TransType.objects.get(name='recharge_amt')
        insert_date = timezone.localtime(timezone.now()).date()

        acct_trans = factory.create_acct_tran(
            hotel=self.hotel,
            trans_type=trans_type,
            insert_date=insert_date
            )

        self.assertIsInstance(acct_trans, AcctTrans)
        self.assertEqual(AcctTrans.objects.count(), 1)
        # object tests
        acct_trans = AcctTrans.objects.first()
        self.assertEqual(acct_trans.trans_type.name, trans_type.name)
        self.assertEqual(acct_trans.amount, 1000)
        self.assertEqual(acct_trans.balance, 1000)
        self.assertEqual(acct_trans.sms_used, 0)
        self.assertEqual(acct_trans.insert_date, insert_date)

    def test_create_account_tran__init_amt(self):
        trans_types = factory.create_trans_types()
        trans_type = TransType.objects.get(name='init_amt')
        insert_date = timezone.localtime(timezone.now()).date()

        acct_trans = factory.create_acct_tran(
            hotel=self.hotel,
            trans_type=trans_type,
            insert_date=insert_date
            )

        self.assertIsInstance(acct_trans, AcctTrans)
        self.assertEqual(AcctTrans.objects.count(), 1)
        # object tests
        acct_trans = AcctTrans.objects.first()
        self.assertEqual(acct_trans.trans_type.name, trans_type.name)
        self.assertEqual(acct_trans.amount, 1000)
        self.assertEqual(acct_trans.balance, 1000)
        self.assertEqual(acct_trans.sms_used, 0)
        self.assertEqual(acct_trans.insert_date, insert_date)

    def test_create_account_tran__sms_used(self):
        trans_types = factory.create_trans_types()
        trans_type = TransType.objects.get(name='sms_used')
        insert_date = timezone.localtime(timezone.now()).date()

        acct_trans = factory.create_acct_tran(
            hotel=self.hotel,
            trans_type=trans_type,
            insert_date=insert_date
            )

        self.assertIsInstance(acct_trans, AcctTrans)
        self.assertEqual(AcctTrans.objects.count(), 1)
        # object tests
        acct_trans = AcctTrans.objects.first()
        self.assertEqual(acct_trans.trans_type.name, trans_type.name)
        self.assertTrue(10 <= acct_trans.sms_used <= 100)
        self.assertEqual(acct_trans.amount, acct_trans.sms_used*settings.DEFAULT_SMS_COST)
        self.assertEqual(acct_trans.balance, acct_trans.sms_used*settings.DEFAULT_SMS_COST)
        self.assertEqual(acct_trans.insert_date, insert_date)

    def test_create_account_tran__phone_number(self):
        trans_types = factory.create_trans_types()
        trans_type = TransType.objects.get(name='phone_number')
        insert_date = timezone.localtime(timezone.now()).date()

        acct_trans = factory.create_acct_tran(
            hotel=self.hotel,
            trans_type=trans_type,
            insert_date=insert_date
            )

        self.assertIsInstance(acct_trans, AcctTrans)
        self.assertEqual(AcctTrans.objects.count(), 1)
        # object tests
        acct_trans = AcctTrans.objects.first()
        self.assertEqual(acct_trans.trans_type.name, trans_type.name)
        self.assertEqual(acct_trans.sms_used, 0)
        self.assertEqual(acct_trans.amount, -(settings.PHONE_NUMBER_MONTHLY_COST))
        self.assertEqual(acct_trans.balance, -(settings.PHONE_NUMBER_MONTHLY_COST))
        self.assertEqual(acct_trans.insert_date, insert_date)




