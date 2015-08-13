from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from main.models import Hotel
from main.tests.factory import create_hotel, create_hotel_user, PASSWORD
from sms.models import PhoneNumber
from sms.tests.factory import create_phone_number
from utils import create


class PhoneNumberTests(TestCase):

    # TODO: Add fixtures b/c will use actual created Twilio Phone
    #   numbers to test "context", etc...
    # fixtures = ['users.json', 'main.json', 'sms.json']

    def setUp(self):
        create._get_groups_and_perms()
        self.password = PASSWORD

        # set User "aaron_test" from fixtures as an attr on this class
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, username='aaron_test', group='hotel_admin')
        self.username = self.user.username

        # Phone
        self.ph_num = create_phone_number(self.hotel)

    def test_fixtures(self):
        self.assertTrue(isinstance(self.user, User))
        self.assertTrue(isinstance(self.hotel, Hotel))
        self.assertTrue(isinstance(self.ph_num, PhoneNumber))

    def test_list(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sms:ph_num_list'))
        self.assertEqual(response.status_code, 200)
        # Context
        assert response.context['headline']
        assert response.context['addit_info']
        assert response.context['phone_numbers']

    def test_add(self):
        # Dave confirms buy
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sms:ph_num_add'))
        self.assertEqual(response.status_code, 200)
        # Context
        assert response.context['addit_info']
        assert response.context['btn_text']

    def test_delete(self):
        # Dave goes to DeleteView
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('sms:ph_num_delete', kwargs={'sid': self.ph_num.sid}))
        self.assertEqual(response.status_code, 200)
        assert response.context['btn_color'] == 'danger'
        assert response.context['btn_text'] == 'Delete'