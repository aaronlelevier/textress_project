from django import forms
from django.test import TestCase
from django.core.urlresolvers import reverse

from account.models import AcctCost, AcctTrans, TransType, TRANS_TYPES, INIT_CHARGE_AMOUNT
from main.tests.factory import create_hotel, create_hotel_user, PASSWORD
from sms.forms import PhoneNumberAddForm
from utils import create


class PhoneNumberAddTests(TestCase):

    fixtures = ['trans_type.json']

    def setUp(self):
        # Hotel
        self.hotel = create_hotel()
        # Account
        self.init_amt, _ = TransType.objects.get_or_create(name='init_amt')
        self.acct_cost, _ = AcctCost.objects.get_or_create(self.hotel, auto_recharge=True)
        self.acct_trans, _ = AcctTrans.objects.get_or_create(self.hotel, self.init_amt)
        # User
        create._get_groups_and_perms()
        self.password = PASSWORD
        self.user = create_hotel_user(self.hotel, username='aaron_test', group='hotel_admin')
        #Login
        self.client.login(username=self.user.username, password=self.password)

    def teardown(self):
        self.client.logout()

    def test_form_success(self):
        # Auto-recharge = True, so this will succeed
        response = self.client.post(reverse('sms:ph_num_add'))
        self.assertEqual(response.status_code, 302)

    def test_form_fail(self):
        # So the Hotel won't have enought to purchase a PH Num
        hotel_account_balance = AcctTrans.objects.balance(self.hotel)

        sms_used, _ = TransType.objects.get_or_create(name='sms_used')
        acct_tran = AcctTrans.objects.create(
            hotel=self.hotel,
            trans_type=sms_used,
            amount= -(hotel_account_balance)
        )

        # setup
        self.acct_cost.auto_recharge = False
        self.acct_cost.save()
        # test
        response = self.client.post(reverse('sms:ph_num_add'))
        self.assertEqual(response.status_code, 200) # 302 redirect would be a success. 
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        self.assertIn("or turn Auto-recharge ON", str(m[0]))
