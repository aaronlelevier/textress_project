import pytest
import twilio

from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from model_mommy import mommy

from main.models import Hotel
from main.tests.factory import (create_hotel, make_subaccount,
    CREATE_USER_DICT, CREATE_HOTEL_DICT)
from sms.models import PhoneNumber
from utils import create
from sms.helpers import sms_messages


class PhoneNumberTests(TestCase):

    # TODO: Add fixtures b/c will use actual created Twilio Phone
    #   numbers to test "context", etc...
    fixtures = ['users.json', 'main.json', 'sms.json']

    def setUp(self):
        create._get_groups_and_perms()
        self.password = '1234'

        # set User "aaron_test" from fixtures as an attr on this class
        self.user = User.objects.get(username='aaron_test')
        # b/c passwords are stored as a hash in json fixtures
        self.user.set_password(self.password)
        self.user.save()

        self.username = self.user.username
        self.hotel = self.user.profile.hotel

        # Phone
        self.ph_num = self.hotel.phonenumbers.primary(hotel=self.hotel)

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