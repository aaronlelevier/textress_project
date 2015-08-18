from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from account.models import AcctCost
from main.models import Hotel
from main.tests.factory import create_hotel, create_hotel_user, PASSWORD
from sms.models import PhoneNumber
from sms.tests.factory import create_phone_number
from utils import create


class PhoneNumberTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.password = PASSWORD
        # set User "aaron_test" from fixtures as an attr on this class
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, username='aaron_test', group='hotel_admin')
        self.username = self.user.username
        # Phone
        self.ph_num = create_phone_number(self.hotel)
        #Login
        self.client.login(username=self.username, password=self.password)

    def teardown(self):
        self.client.logout()

    ### LIST

    def test_list_response(self):
        response = self.client.get(reverse('sms:ph_num_list'))
        self.assertEqual(response.status_code, 200)

    def test_list_context(self):
        response = self.client.get(reverse('sms:ph_num_list'))
        self.assertTrue(response.context['headline'])
        self.assertTrue(response.context['addit_info'])
        self.assertTrue(response.context['phone_numbers'])

    ### ADD

    def test_add_response(self):
        response = self.client.get(reverse('sms:ph_num_add'))
        self.assertEqual(response.status_code, 200)

    def test_add_context(self):
        response = self.client.get(reverse('sms:ph_num_add'))
        self.assertTrue(response.context['headline'])
        self.assertTrue(response.context['addit_info'])
        self.assertTrue(response.context['btn_text'])

    def test_add_context_form(self):
        response = self.client.get(reverse('sms:ph_num_add'))
        self.assertTrue(response.context['form'])
        self.assertIsInstance(response.context['form'].hotel, Hotel)

    def test_add_form(self):
        # TODO: Test Form Validation
        # acct_cost, created = AcctCost.objects.get_or_create(self.hotel)
        # print self.hotel.acct_cost.__dict__
        # assert 1 == 2

    ### DELETE

    def test_delete(self):
        # Dave goes to DeleteView
        response = self.client.get(reverse('sms:ph_num_delete', kwargs={'sid': self.ph_num.sid}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['btn_color']) == 'danger'
        self.assertTrue(response.context['btn_text']) == 'Delete'