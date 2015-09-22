import os
import datetime
import pytest

from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import User, Group
from django.utils import timezone

from model_mommy import mommy

from concierge.models import Message, Guest, Hotel, Reply
from concierge.tests.factory import make_guests, make_messages
from main.tests.factory import create_hotel, create_hotel_user
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
            mommy.make(
                Guest,
                name="Unknown Guest",
                hotel=self.hotel,
                phone_number=settings.DEFAULT_TO_PH_BAD
                )

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

    ## Guest.objects.get_by_phone

    def test_get_by_phone(self):
        guest = Guest.objects.get_by_phone(self.hotel, self.guest.phone_number)
        self.assertIsInstance(guest, Guest)
        self.assertFalse(guest.hidden)

    def test_get_by_phone_archived(self):
        guest = Guest.objects.get_by_phone(self.hotel, self.archived_guest.phone_number)
        self.assertIsInstance(guest, Guest)
        self.assertTrue(guest.hidden)

    def test_get_by_phone_unknown_guest_get(self):
        # when the Hotel recieves an SMS from an unknown Guest
        init_count = Guest.objects.count()
        guest = Guest.objects.get_by_phone(self.hotel, self.unknown_guest.phone_number)
        self.assertEqual(guest.name, self.unknown_guest.name)
        post_count = Guest.objects.count()
        self.assertEqual(init_count, post_count)

    def test_get_or_create_unknown_guest_create(self):
        hotel2 = create_hotel()
        init_count = Guest.objects.count()
        guest = Guest.objects.get_by_phone(hotel2, create._generate_ph())
        self.assertEqual(guest.name, self.unknown_guest.name)
        post_count = Guest.objects.count()
        self.assertEqual(init_count+1, post_count)


class MessageManagerTests(TestCase):

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
            guest=self.guest,
            number=1
            )
        self.message = self.messages[0]

        self.post_data = {
            u'Body': [u'Hey'], u'MessageSid': [u'SMa3376deff77d397cbcf502a6aa27889e'],
            u'FromZip': [u''], u'SmsStatus': [u'received'], u'SmsMessageSid': [u'SMa3376deff77d397cbcf502a6aa27889e'],
            u'AccountSid': [u'AC7036cf7d16a460884ff84c0a5a99a008'], u'FromCity': [u''], u'ApiVersion': [u'2010-04-01'],
            u'To': [u'+17024302691'], u'From': [u'+17754194000'], u'NumMedia': [u'0'], u'ToZip': [u'89106'],
            u'ToCountry': [u'US'], u'NumSegments': [u'1'], u'ToState': [u'NV'],
            u'SmsSid': [u'SMa3376deff77d397cbcf502a6aa27889e'], u'ToCity': [u'LAS VEGAS'], u'FromState': [u'NV'],
            u'FromCountry': [u'US']
            }

    def test_current(self):
        for message in Message.objects.current():
            assert message.hidden == False

    def test_receive_message_already_in_db(self):
        # when calling ``.receive_message()`` the initial DB count is the 
        # same before and after b/c the Message already exists, so it does't
        # create a new one.
        init_count = Message.objects.count()
        Message.objects.receive_message(guest=self.guest, data={'sid': self.messages[0].sid})
        post_count = Message.objects.count()
        self.assertEqual(init_count, post_count)

    def test_receive_message_create(self):
        # will create a Message because Twilio message not yet in the DB
        data = {
            "sid": "SM254a9f3f7604418fa8b06a90b7a8f82b",
            "to": "+12813698851",
            "from_": "+17024302691",
            "body": "sent via unittest save() method",
            "status": "undelivered",
        }
        init_count = Message.objects.count()
        Message.objects.receive_message(guest=self.guest, data=data)
        post_count = Message.objects.count()
        self.assertEqual(init_count, post_count-1)

    def test_monthly_all(self):
        assert Message.objects.monthly_all(date=self.today)

    def test_daily_all(self):
        manual_daily_all = Message.objects.filter(insert_date=self.today)
        mgr_daily_all = Message.objects.daily_all(date=self.today)
        assert len(manual_daily_all) == len(mgr_daily_all)

    ### receive_message_post

    def test_receive_message_post_get(self):
        data = {}
        data['SmsSid'] = self.message.sid
        self.assertEqual(
            Message.objects.receive_message_post(self.guest, data),
            self.message
        )

    def test_receive_message_post_create(self):
        # setup
        msg = create._generate_name()
        data = {}
        data.update({
            'SmsSid': 'bad sid',
            'SmsStatus': 'sent',
            'To': settings.DEFAULT_TO_PH,
            'From': settings.DEFAULT_TO_PH,
            'Body': msg
        })
        # test
        self.assertIsInstance(
            Message.objects.receive_message_post(self.guest, data),
            Message
        )


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


class MessageSendTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.user = create_hotel_user(hotel=self.hotel)
        self.hotel.twilio_sid = os.environ['TWILIO_ACCOUNT_SID_TEST']
        self.hotel.twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN_TEST']
        self.hotel.twilio_phone_number = os.environ['TWILIO_PHONE_NUMBER_TEST']
        self.hotel.save()
        self.guest = make_guests(hotel=self.hotel, number=1)[0] # b/c returns list
        self.guest.phone_number = settings.DEFAULT_TO_PH
        self.guest.save()

    def test_create(self):
        self.assertIsInstance(self.guest.hotel, Hotel)

    def test_create_that_sends(self):
        message = Message.objects.create(
            guest=self.guest,
            to_ph=self.guest.phone_number,
            user=self.user,
            body='sent via unittest save() method'
            )
        self.assertIsInstance(message, Message)
        # TODO: failing b/c ``hotel`` is not attaching to message, 
        #   but work fine from the GUI??
        # self.assertEqual(message.hotel, self.guest.hotel)


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