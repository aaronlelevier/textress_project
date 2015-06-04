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
from utils import create
from sms.models import Text, DemoCounter
from sms.helpers import sms_messages


class PhoneNumberTests(TestCase):

    # TODO: Add fixtures b/c will use actual created Twilio Phone
    #   numbers to test "context", etc...

    def setUp(self):
        create._get_groups_and_perms()
        self.username = 'test'
        self.password = '1234'

        # Creates a Admin User and Hotel Object - needed to view PhoneNumber Views
        # Step 1
        response = self.client.post(reverse('main:register_step1'),
            CREATE_USER_DICT)
        self.client.login(username=self.username, password=self.password)
        # Step 2
        response = self.client.post(reverse('main:register_step2'),
            CREATE_HOTEL_DICT)

    def test_list(self):
        response = self.client.get(reverse('sms:ph_num_list'))
        self.assertEqual(response.status_code, 200)
        assert response.context['headline']

    def test_select(self):
        # Dave can see a list of ph numbers
        response = self.client.get(reverse('sms:ph_num_select'))
        self.assertEqual(response.status_code, 200)

    def test_add(self):
        # Dave confirms buy
        response = self.client.get(reverse('sms:ph_num_add'))














