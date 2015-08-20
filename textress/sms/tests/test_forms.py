from django import forms
from django.test import TestCase
from django.core.urlresolvers import reverse

from account.models import AcctCost, AcctTrans, TransType, TRANS_TYPES
from main.tests.factory import create_hotel, create_hotel_user, PASSWORD
from sms.forms import PhoneNumberAddForm
from utils import create


class FormTests(TestCase):

    def setUp(self):
        # Hotel
        self.hotel = create_hotel()
        # Account
        self.acct_cost, _ = AcctCost.objects.get_or_create(self.hotel, auto_recharge=False)
        self.init_amt = TransType.objects.create(name=TRANS_TYPES[0][0], desc=TRANS_TYPES[0][0])
        self.acct_trans, _ = AcctTrans.objects.get_or_create(self.hotel, self.init_amt)
        # User
        create._get_groups_and_perms()
        self.password = PASSWORD
        self.user = create_hotel_user(self.hotel, username='aaron_test', group='hotel_admin')
        #Login
        self.client.login(username=self.user.username, password=self.password)

    def teardown(self):
        self.client.logout()

    def test_form(self):
        # Initial AcctCost is created with a balance of 200, but the PH 
        # cost is 300, so this should raise an error when trying to buy 
        # a new phone number.
        response = self.client.post(reverse('sms:ph_num_add'))
        self.assertEqual(response.status_code, 200) # 302 redirect would be a success. 
                                                    # In this case goes back to form to display error

        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        self.assertIn("or turn Auto-recharge ON", str(m[0]))