import pytest
import requests

import twilio
from twilio.rest import TwilioRestClient

from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group

from model_mommy import mommy

from sms.models import Text
from sms.helpers import send_text, get_weather, sms_messages, send_message
from main.models import Hotel
from main.tests.test_models import create_hotel
from utils import create


class GeneralTests(TestCase):

    def test_get_weather(self):
        assert "Yahoo!" in get_weather()

    def test_sms_messages(self):
        assert sms_messages


class SendMessageTests(TestCase):
    '''
    test ``sms.helpers.send_message(hotel, to, body)``

    send as:
        Two different Hotels
        View POST
    '''

    def setUp(self):
        self.password = '1234'
        self.hotel = create_hotel()
        self.other_hotel = create_hotel('other')

        # create "Hotel Manager" Group
        create._get_groups_and_perms()

        # Admin
        self.admin = mommy.make(User, username='admin')
        self.admin.groups.add(Group.objects.get(name="hotel_admin"))
        self.admin.set_password(self.password)
        self.admin.save()
        self.admin.profile.update_hotel(hotel=self.hotel)
        # Hotel Admin ID
        self.hotel.admin_id = self.admin.id
        self.hotel.save()

        # Manager
        self.mgr = mommy.make(User, username='mgr')
        self.mgr.groups.add(Group.objects.get(name="hotel_manager"))
        self.mgr.set_password(self.password)
        self.mgr.save()
        self.mgr.profile.update_hotel(hotel=self.hotel)

        # User
        self.user = mommy.make(User, username='user')
        self.user.set_password(self.password)
        self.user.save()
        self.user.profile.update_hotel(hotel=self.hotel)

        # Other Hotel Admin
        self.other_admin = mommy.make(User, username='other_admin')
        self.other_admin.groups.add(Group.objects.get(name="hotel_admin"))
        self.other_admin.set_password(self.password)
        self.other_admin.save()
        self.other_admin.profile.update_hotel(hotel=self.other_hotel)

        # Configure Twilio attrs
        account = settings.TWILIO_ACCOUNT_SID
        token = settings.TWILIO_AUTH_TOKEN
        client = TwilioRestClient(account, token)
        # hotel == Dave Hotel
        subaccount = client.accounts.list(friendly_name="Dave Hotel")[0]
        self.hotel.twilio_sid = subaccount.sid
        self.hotel.twilio_auth_token = subaccount.auth_token
        self.hotel.twilio_phone_number = subaccount.incoming_phone_numbers.list()[0].phone_number
        self.hotel.save()
        # other_hotel = JohnA Hotel
        subaccount = client.accounts.list(friendly_name="JohnA Hotel")[0]
        self.other_hotel.twilio_sid = subaccount.sid
        self.other_hotel.twilio_auth_token = subaccount.auth_token
        self.other_hotel.twilio_phone_number = subaccount.incoming_phone_numbers.list()[0].phone_number
        self.other_hotel.save()

    def test_send_message(self):
        message = send_message(hotel=self.hotel, to=settings.DEFAULT_TO_PH,
            body='sms.test.test_helpers msg')
        assert message