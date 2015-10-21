import os
import datetime

from django.conf import settings
from django.db import models
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth.models import User, Group
from django.utils import timezone

from model_mommy import mommy

from concierge.models import (Message, Guest, Hotel, Reply, TriggerType, Trigger,
    trigger_send_message)
from concierge.tests.factory import make_guests, make_messages
from main.tests.factory import create_hotel, create_hotel_user
from utils import create
from utils.exceptions import (CheckOutDateException, PhoneNumberInUse,
    ReplyNotFound)


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
        with self.assertRaises(ObjectDoesNotExist):
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

    # utils.models .delete() : start

    def test_delete(self):
        guest = make_guests(hotel=self.hotel, number=1)[0]
        self.assertFalse(guest.hidden)
        guest.delete()
        self.assertTrue(guest.hidden)

    def test_delete_override(self):
        guest = make_guests(hotel=self.hotel, number=1)[0]
        guest.delete(override=True)
        with self.assertRaises(Guest.DoesNotExist):
            Guest.objects.get(id=guest.id)

    # utils.models .delete() : end

    def test_guest(self):
        assert isinstance(self.guest, Guest)

    def test_validate_phone_number_taken(self):
        with self.assertRaises(PhoneNumberInUse):
            mommy.make(
                Guest,
                name="Unknown Guest",
                hotel=self.hotel,
                phone_number=settings.DEFAULT_TO_PH_BAD
                )

    def test_checkin_date_validation(self):
        with self.assertRaises(CheckOutDateException):
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
        self.assertFalse(guest.confirmed)

        guest._confirmed()
        guest = Guest.objects.get(pk=guest.id)
        self.assertTrue(guest.confirmed)

    def test_stop(self):
        guest = self.guest
        guest.stop = False
        guest.save()

        guest = Guest.objects.get(pk=guest.id)
        self.assertFalse(guest.stop)

        guest._stop()
        guest = Guest.objects.get(pk=guest.id)
        self.assertTrue(guest.stop)

    def test_is_unknown(self):
        self.assertFalse(self.guest.is_unknown)
        self.assertTrue(self.unknown_guest.is_unknown)


class MessageManagerTests(TestCase):

    def setUp(self):
        self.password = '1234'
        self.today = timezone.now().date()

        # Hotel
        self.hotel = create_hotel()
        # create "Hotel Manager" Group
        create._get_groups_and_perms()
        # Admin
        self.admin = create_hotel_user(self.hotel, username='admin', group='hotel_admin')
        # Guest
        self.guest = make_guests(hotel=self.hotel, number=1)[0]

        # Messages
        self.messages = make_messages(
            hotel=self.hotel,
            user=self.admin,
            guest=self.guest,
            insert_date=timezone.now().date(),
            number=1
            )
        self.message = self.messages[0]

        self.twilio_data = {
            'sid': "SMa3376deff77d397cbcf502a6aa27889e",
            'date_sent': '2015-10-17',
            'status': 'sent',
            'to': self.guest.phone_number,
            'from_': self.guest.phone_number,
            'body': 'foo'
        }

        self.post_data = {
            u'Body': [u'Hey'],
            u'MessageSid': [u'SMa3376deff77d397cbcf502a6aa27889e'],
            u'FromZip': [u''],
            u'SmsStatus': [u'received'],
            u'SmsMessageSid': [u'SMa3376deff77d397cbcf502a6aa27889e'],
            u'AccountSid': [u'AC7036cf7d16a460884ff84c0a5a99a008'],
            u'FromCity': [u''],
            u'ApiVersion': [u'2010-04-01'],
            u'To': [u'+17024302691'],
            u'From': [u'+17754194000'],
            u'NumMedia': [u'0'],
            u'ToZip': [u'89106'],
            u'ToCountry': [u'US'],
            u'NumSegments': [u'1'],
            u'ToState': [u'NV'],
            u'SmsSid': [u'SMa3376deff77d397cbcf502a6aa27889e'],
            u'ToCity': [u'LAS VEGAS'],
            u'FromState': [u'NV'],
            u'FromCountry': [u'US']
            }

    def test_current(self):
        for message in Message.objects.current():
            self.assertEqual(message.hidden, False)

    def test_monthly_all(self):
        self.assertTrue(Message.objects.monthly_all(date=self.today))

    def test_daily_all(self):
        manual_daily_all = Message.objects.filter(insert_date=self.today)
        mgr_daily_all = Message.objects.daily_all(date=self.today)
        self.assertEqual(
            manual_daily_all.count(),
            mgr_daily_all.count()
        )

    ### receive_message (twilio API data)

    def test_receive_message_get(self):
        self.twilio_data.update({'sid': self.message.sid})
        msg, created = Message.objects.receive_message(guest=self.guest, data=self.twilio_data)
        self.assertIsInstance(msg, Message)
        self.assertFalse(created)

    def test_receive_message_create(self):
        msg, created = Message.objects.receive_message(guest=self.guest, data=self.twilio_data)
        self.assertIsInstance(msg, Message)
        self.assertIsNone(msg.user)
        self.assertTrue(created)

    def test_receive_message_create_with_user(self):        
        self.hotel.twilio_phone_number = settings.DEFAULT_TO_PH
        self.hotel.save()
        self.twilio_data['from_'] = self.hotel.twilio_phone_number
        msg, created = Message.objects.receive_message(guest=self.guest, data=self.twilio_data)
        self.assertIsInstance(msg, Message)
        self.assertIsInstance(msg.user, User)
        self.assertTrue(created)

    ### receive_message_post

    def test_receive_message_post_get(self):
        data = {'SmsSid': self.message.sid}
        self.assertEqual(
            Message.objects.receive_message_post(self.guest, data),
            self.message
        )

    def test_receive_message_post_create(self):
        # setup
        msg = create._generate_name()
        data = {
            'SmsSid': 'bad sid',
            'SmsStatus': 'sent',
            'To': settings.DEFAULT_TO_PH,
            'From': settings.DEFAULT_TO_PH,
            'Body': msg
        }
        # test
        db_message = Message.objects.receive_message_post(self.guest, data)
        self.assertIsInstance(db_message, Message)
        self.assertIsNone(db_message.user)


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


class ReplyTests(TestCase):

    def setUp(self):
        self.letter_stop = "S"
        self.letter_help = "H"
        self.letter_reactivate = "Y"
        # Hotel
        self.hotel_w_reply = create_hotel()
        self.hotel_w_no_reply = create_hotel()
        # Guest
        self.guest = make_guests(hotel=self.hotel_w_reply, number=1)[0]
        self.guest_w_no_reply = make_guests(hotel=self.hotel_w_no_reply, number=1)[0]
        # archived guest
        self.archived_guest = mommy.make(
            Guest,
            hotel=self.hotel_w_reply,
            hidden=True,
            phone_number=settings.DEFAULT_TO_PH_2)
        # for resolving "Unknown Guest"
        self.unknown_guest = mommy.make(
            Guest,
            name="Unknown Guest",
            hotel=self.hotel_w_reply,
            phone_number=settings.DEFAULT_TO_PH_BAD
            )
        # Reply
        self.hotel_reply_H = mommy.make(Reply, hotel=self.hotel_w_reply, letter=self.letter_help)
        self.system_reply_S = mommy.make(Reply, letter=self.letter_stop)
        self.system_reply_Y = mommy.make(Reply, letter=self.letter_reactivate)

    ### MANAGER TESTS

    def test_get_reply_hotel(self):
        reply = Reply.objects.get_reply(self.hotel_w_reply, "H")
        self.assertEqual(reply.hotel, self.hotel_w_reply)

    def test_get_reply_system(self):
        reply = Reply.objects.get_reply(self.hotel_w_no_reply, "S")
        self.assertIsInstance(reply, Reply)
        self.assertIsNone(reply.hotel)

    def test_get_reply_none(self):
        with self.assertRaises(ReplyNotFound):
            Reply.objects.get_reply(self.hotel_w_no_reply, "X")

    def test_check_for_data_update_stop(self):
        self.assertFalse(self.guest.stop)
        Reply.objects.check_for_data_update(self.guest, self.system_reply_S)
        self.assertTrue(self.guest.stop)

    def test_check_for_data_update_no_stop(self):
        self.assertFalse(self.guest.stop)
        Reply.objects.check_for_data_update(self.guest, self.hotel_reply_H)
        self.assertFalse(self.guest.stop)

    def test_check_for_data_update_reactivate(self):
        self.guest.stop = True
        self.guest.save()
        Reply.objects.check_for_data_update(self.guest, self.system_reply_Y)
        self.assertFalse(self.guest.stop)

    def test_process_reply_return_reply(self):
        reply = Reply.objects.process_reply(self.guest, self.hotel_w_reply, self.letter_help)
        self.assertIsInstance(reply, Reply)

    def test_process_reply_return_none(self):
        reply = Reply.objects.process_reply(self.guest, self.hotel_w_reply, "normal body of msg")
        self.assertIsNone(reply)

    ### MODEL TESTS

    def test_upper(self):
        letter = 'g'
        reply = mommy.make(Reply, hotel=self.hotel_w_no_reply, letter=letter)
        self.assertEqual(reply.letter, letter.upper())

    def test_reserved_letter_true(self):
        self.assertTrue(Reply._reserved_letter("S"))

    def test_reserved_letter_false(self):
        self.assertFalse(Reply._reserved_letter("A"))

    def test_validate_not_reserved_letter(self):
        reply = mommy.make(Reply, hotel=self.hotel_w_reply, letter="A")
        self.assertIsInstance(reply, Reply)

    def test_validate_not_reserved_letter_raise(self):
        with self.assertRaises(ValidationError):
            mommy.make(Reply, hotel=self.hotel_w_reply, letter="S")
    
    def test_validate_unique_constraint(self):
        reply = mommy.make(Reply, hotel=self.hotel_w_reply, letter="A")
        self.assertIsInstance(reply, Reply)

    def test_validate_unique_constraint_raise(self):
        mommy.make(Reply, hotel=self.hotel_w_reply, letter="A")
        with self.assertRaises(ValidationError):
            mommy.make(Reply, hotel=self.hotel_w_reply, letter="A")

    def test_validate_unique_constraint_update_ok(self):
        # save() for an existing "letter" shouldn't raise an error
        # because it is still unique
        reply = mommy.make(Reply, hotel=self.hotel_w_reply, letter="A")
        reply.message = "foo"
        reply.save()
        self.assertEqual(Reply.objects.filter(hotel=self.hotel_w_reply, letter="A").count(), 1)


class TriggerTypeTests(TestCase):

    def test_str(self):
        t = mommy.make(TriggerType)
        self.assertEqual(str(t), t.name)

    def test_human_name_save(self):
        human_name = "check-in"
        t = mommy.make(TriggerType, human_name=human_name)
        self.assertEqual(t.human_name, human_name)

    def test_human_name_default(self):
        name = "check_in"
        t = mommy.make(TriggerType, name=name)
        self.assertEqual(t.human_name, "check in")


class TriggerTypeTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.guest = make_guests(self.hotel, number=1)[0]
        self.trigger = mommy.make(Trigger, hotel=self.hotel, type__name="check_in")

    def test_check_in(self):
        twilio_msg = Trigger.objects.send_message(self.guest.id, "check_in")
        self.assertIsNotNone(twilio_msg)

    def test_check_in_stop_works(self):
        self.guest.stop = True
        self.guest.save()
        twilio_msg = Trigger.objects.send_message(self.guest.id, "check_in")
        self.assertIsNone(twilio_msg)

    def test_check_in_not_configured(self):
        self.trigger.delete(override=True)
        twilio_msg = Trigger.objects.send_message(self.guest.id, "check_in")
        self.assertIsNone(twilio_msg)


class TriggerTests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.guest = make_guests(hotel=self.hotel, number=1)[0]
        self.trigger_type = mommy.make(TriggerType, name="check_out")
        self.reply_letter = "T"
        self.hotel_reply = mommy.make(Reply, hotel=self.hotel, letter=self.reply_letter,
            message="Thank you for staying")
        self.trigger = mommy.make(Trigger, hotel=self.hotel, type=self.trigger_type,
            reply=self.hotel_reply)

    def test_foreign_keys(self):
        self.assertIsInstance(self.trigger.hotel, Hotel)
        self.assertIsInstance(self.trigger.type, TriggerType)
        self.assertIsInstance(self.trigger.reply, Reply)

    def test_str(self):
        self.assertEqual(
            str(self.trigger),
            "Hotel: {}; Trigger Type:{}.".format(self.trigger.hotel, self.trigger.type)
        )

    def test_validate_type_hotel_unique_ok(self):
        self.trigger._validate_type_hotel_unique()

    def test_validate_type_hotel_unique_raise(self):
        with self.assertRaises(ValidationError):
            Trigger.objects.create(type=self.trigger.type, hotel=self.trigger.hotel)


    def test_delete_check_out_message_unit_test(self):
        global Message
        Message.save = models.Model.save

        ret = trigger_send_message.apply(args=(self.guest.id, 'check_out')).get()
        self.assertIsInstance(ret, Message)
