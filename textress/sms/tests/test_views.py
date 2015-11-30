from mock import MagicMock, PropertyMock
from mock import patch

from django.test import TestCase
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from model_mommy import mommy

from account.models import AcctCost, AcctTrans, TransType, Pricing
from account.tests.factory import create_trans_types
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
        self.acct_cost = mommy.make(AcctCost, hotel=self.hotel)
        create_trans_types()
        self.pricing = mommy.make(Pricing, hotel=self.hotel)
        self.user = create_hotel_user(self.hotel, username='aaron_test', group='hotel_admin')
        self.username = self.user.username
        # Phone
        self.ph_num = create_phone_number(self.hotel)
        #Login
        self.client.login(username=self.username, password=self.password)

        # clear cache for TransTypes
        cache.clear()

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

    def test_twilio_phone_alert(self):
        response = self.client.get(reverse('sms:ph_num_list'))
        self.assertTrue(response.context['alerts'])

        self.hotel.twilio_ph_sid = self.ph_num.sid
        self.hotel.save()

        response = self.client.get(reverse('sms:ph_num_list'))
        with self.assertRaises(KeyError):
            response.context['alerts']

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

    @patch("sms.models.PhoneNumberManager.purchase_number")
    def test_add_phone_number__creates_acct_trans(self, purchase_number_mock):
        self.assertEqual(AcctTrans.objects.filter(hotel=self.hotel,
            trans_type__name='phone_number').count(), 0)

        response = self.client.post(reverse('sms:ph_num_add'), {}, follow=True)

        self.assertRedirects(response, reverse('sms:ph_num_list'))
        self.assertTrue(purchase_number_mock.called)

    ### DELETE

    def test_delete(self):
        # Dave goes to DeleteView
        response = self.client.get(reverse('sms:ph_num_delete', kwargs={'sid': self.ph_num.sid}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['btn_color']) == 'danger'
        self.assertTrue(response.context['btn_text']) == 'Delete'
