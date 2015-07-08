import os
import time
import pytest
import stripe

from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group

from model_mommy import mommy

from account.tests.factory import CREATE_ACCTCOST_DICT
from main.tests.factory import (CREATE_USER_DICT, CREATE_HOTEL_DICT, PASSWORD,
    create_hotel, create_hotel_user)
from utils import create


class StripeMixinTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.username = CREATE_USER_DICT['username']
        self.password = '1234'

        # Step 1
        response = self.client.post(reverse('main:register_step1'),
            CREATE_USER_DICT)
        self.client.login(username=self.username, password=self.password)
        # Step 2
        response = self.client.post(reverse('main:register_step2'),
            CREATE_HOTEL_DICT)
        # Step 3
        response = self.client.post(reverse('register_step3'), # no namespace b/c in "account" app
            CREATE_ACCTCOST_DICT)

    def test_stripe_context(self):
        # StripeMixin #
        response = self.client.get(reverse('payment:register_step4'))
        self.assertEqual(response.context['publishable_key'], settings.STRIPE_PUBLIC_KEY)


