import random
import datetime
import pytest
from twilio.rest import TwilioRestClient

from django import forms
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import User, Group
from django.http import Http404
from django.utils import timezone

from model_mommy import mommy

from concierge.models import Message, Guest, Hotel, Reply
from concierge.tests.factory import make_guests, make_messages
from main.tests.factory import create_hotel
from utils import create
from utils.exceptions import (CheckOutDateException, PhoneNumberInUse,
    ReplyNotFound)


class GuestTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.guest = make_guests(hotel=self.hotel, number=1)[0] # b/c returns list

        # archived guest
        self.archived_guest = mommy.make(Guest, hotel=self.hotel, hidden=True,
            phone_number=settings.DEFAULT_TO_PH_2)

        # for resolving "Unknown Guest"
        self.unknown_guest = mommy.make(
            Guest,
            name="Unknown Guest",
            hotel=self.hotel,
            phone_number=settings.DEFAULT_TO_PH_BAD
            )

    def test_guest(self):
        assert isinstance(self.guest, Guest)

    def test_validate_phone_number_taken(self):
        with pytest.raises(PhoneNumberInUse):
            make_guests(hotel=self.hotel, number=1)

    def test_checkin_date_validation(self):
        with pytest.raises(CheckOutDateException):
            self.guest.check_out = timezone.now().date() + datetime.timedelta(days=-2)
            ci, co = self.guest.validate_check_in_out(self.guest.check_in, self.guest.check_out)

    def test_get_absolute_url(self):
        assert (self.guest.get_absolute_url() ==
                reverse('concierge:guest_detail', kwargs={'pk':self.guest.pk}))

    def test_confirmed(self):
        guest = self.guest
        guest.confirmed = False
        guest.save()

        guest = Guest.objects.get(pk=guest.id)
        assert not guest.confirmed

        guest._confirmed()
        guest = Guest.objects.get(pk=guest.id)
        assert guest.confirmed

    def test_stop(self):
        guest = self.guest
        guest.stop = False
        guest.save()

        guest = Guest.objects.get(pk=guest.id)
        assert not guest.stop

        guest._stop()
        guest = Guest.objects.get(pk=guest.id)
        assert guest.stop

    def test_is_unknown(self):
        assert self.unknown_guest.is_unknown


class GuestManagerTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.guest = make_guests(hotel=self.hotel, number=1)[0] # b/c returns list

        # archived guest
        self.archived_guest = mommy.make(Guest, hotel=self.hotel, hidden=True,
            phone_number=settings.DEFAULT_TO_PH_2)

        # for resolving "Unknown Guest"
        self.unknown_guest = mommy.make(
            Guest,
            name="Unknown Guest",
            hotel=self.hotel,
            phone_number=settings.DEFAULT_TO_PH_BAD
            )

    def test_guests(self):
        assert len(Guest.objects.current()) == 2
        assert len(Guest.objects.archived()) == 1

    def test_get_by_hotel_phone(self):
        guest = Guest.objects.get_by_hotel_phone(self.hotel, self.guest.phone_number)
        assert isinstance(guest, Guest)

    def test_get_by_hotel_phone_fail(self):
        with pytest.raises(ObjectDoesNotExist):
            Guest.objects.get_by_hotel_phone(self.hotel, 'wrong_num')

    def test_get_by_phone(self):
        guest = Guest.objects.get_by_phone(self.hotel, self.guest.phone_number)
        assert isinstance(guest, Guest)
        assert not guest.hidden

    def test_get_by_phone_archived(self):
        guest = Guest.objects.get_by_phone(self.hotel, self.archived_guest.phone_number)
        assert isinstance(guest, Guest)
        assert guest.hidden

    def test_get_by_phone_unknown(self):
        # when the Hotel recieves an SMS from an unknown Guest
        guest = Guest.objects.get_by_phone(self.hotel, create._generate_ph())
        self.assertEqual(guest.name, self.unknown_guest.name)


class MessageTests(TestCase):

    def setUp(self):
        self.password = '1234'
        self.today = timezone.now().date()

        # Hotel
        self.hotel = create_hotel()

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

        # Guest
        self.guest = make_guests(hotel=self.hotel, number=1)[0] #b/c returns a list

        # Messages
        self.messages = make_messages(
            hotel=self.hotel,
            user=self.admin,
            guest=self.guest
            )

    def test_create(self):
        for message in self.messages:
            assert isinstance(message, Message)
            assert (message.guest or message.user)

        assert len(self.messages) == 10

    def test_guest_hotel(self):
        assert self.guest.hotel

    def test_msg_short(self):
        message = self.messages[0]
        assert message.msg_short() == "{}...".format(' '.join(message.body.split()[:5]))

    ### MANAGER ###

    def test_monthly_all(self):
        assert Message.objects.monthly_all(date=self.today)

    def test_daily_all(self):
        manual_daily_all = Message.objects.filter(insert_date=self.today)
        mgr_daily_all = Message.objects.daily_all(date=self.today)
        assert len(manual_daily_all) == len(mgr_daily_all)

    def test_current(self):
        for message in Message.objects.current():
            assert message.hidden == False


class MessageSendTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.guest = make_guests(hotel=self.hotel, number=1)[0] # b/c returns list

    def test_create_that_sends(self):
        message = Message.objects.create(
            guest=self.guest,
            to_ph=self.guest.phone_number,
            body='sent via unittest save() method'
            )
        assert isinstance(message, Message)
        assert message.hotel == self.guest.hotel


class ReplyManagerTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.textress = create_hotel(name=settings.TEXTRESS_HOTEL)

        # reserved letter `Reply`. Can only be created if using "Textress Hotel" 
        # as configured in the settings.py
        self.stop_reply = mommy.make(Reply, hotel=self.textress, letter='S',
            func_call='_stop')

        # non-reserved letter `Reply`
        self.help_reply = mommy.make(Reply, hotel=self.hotel, letter='H')

        self.guest = make_guests(hotel=self.hotel, number=1)[0] # b/c returns list

        # archived guest
        self.archived_guest = mommy.make(Guest, hotel=self.hotel, hidden=True,
            phone_number=settings.DEFAULT_TO_PH_2)

        # for resolving "Unknown Guest"
        self.unknown_guest = mommy.make(
            Guest,
            name="Unknown Guest",
            hotel=self.hotel,
            phone_number=settings.DEFAULT_TO_PH_BAD
            )

    def test_reply_hotel(self):
        reply = Reply.objects.get_hotel_reply('H', hotel=self.hotel)
        assert isinstance(reply, Reply)

    def test_reply_textress(self):
        reply = Reply.objects.get_hotel_reply('S')
        assert isinstance(reply, Reply)

    def test_reply_none(self):
        with pytest.raises(ObjectDoesNotExist):
            Reply.objects.get_hotel_reply('N')

    def test_get_reply(self):
        reply = Reply.objects.get_reply(self.guest, self.hotel, 'H')
        assert isinstance(reply, Reply)

    def test_get_reply_default(self):
        # the 'S' letter is reserved, so should resolve to the 
        #   "Textress Hotel's" reserved replies container
        reply = Reply.objects.get_reply(self.guest, self.hotel, 'S')
        assert isinstance(reply, Reply)
        assert reply.hotel.is_textress

    def test_get_reply_none(self):
        with pytest.raises(ReplyNotFound):
            reply = Reply.objects.get_reply(self.guest, self.hotel,
                'This is a standard message.')

    def test_exec_func_call(self):
        assert not self.guest.stop

        Reply.objects.exec_func_call(self.guest, self.guest.hotel,
            self.stop_reply)
        guest = Guest.objects.get(pk=self.guest.id)
        assert self.guest.stop

    def test_process_reply(self):
        reply = Reply.objects.process_reply(self.guest, self.hotel, 'S')
        assert isinstance(reply, Reply)

    def test_process_reply(self):
        reply = Reply.objects.process_reply(self.guest, self.hotel, 'X')
        assert not reply


class ReplyTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()

    def test_upper(self):
        letter = 'g'
        reply = mommy.make(Reply, hotel=self.hotel, letter=letter)
        assert reply.letter == letter.upper()

    def test_reserved_letter(self):
        letter = 's'
        with self.assertRaises(ValidationError):
            mommy.make(Reply, hotel=self.hotel, letter=letter)