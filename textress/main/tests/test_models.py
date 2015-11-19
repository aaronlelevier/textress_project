import os
import random

from django.conf import settings
from django.test import TestCase
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User, Group
from django.utils import timezone

from model_mommy import mommy
from twilio.rest import TwilioRestClient

from account.models import AcctTrans, TransType, AcctCost
from concierge.tests.factory import make_guests, make_messages
from main.models import TwilioClient, Hotel, UserProfile, Subaccount
from main.tests.factory import (create_hotel, create_hotel_user, PASSWORD,
    make_subaccount)
from payment.models import Customer
from utils import create


class TwilioClientTests(TestCase):

    def test_client(self):
        tc = TwilioClient()
        self.assertIsInstance(tc, TwilioClient)
        self.assertIsInstance(tc.client, TwilioRestClient)


class HotelTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.password = PASSWORD
        self.hotel = create_hotel()
        self.dave_hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, group="hotel_admin")
        self.user = create_hotel_user(self.hotel)

        self.sub = make_subaccount(self.hotel, live=True)

        # AcctTrans, TransType, etc...
        self.sms_used, _ = TransType.objects.get_or_create(name='sms_used')
        # Guest
        self.guest = make_guests(hotel=self.hotel, number=1)[0] #b/c returns a list
        # Messages
        self.messages = make_messages(
            insert_date=timezone.now().date(),
            hotel=self.hotel,
            user=self.admin,
            guest=self.guest
        )

    def test_create(self):
        self.assertIsInstance(self.hotel, Hotel)
        self.assertIsInstance(self.user, User)
        self.assertNotEqual(self.hotel.name, self.dave_hotel.name)

    def test_twilio_client(self):
        self.assertIsInstance(self.hotel._client, TwilioRestClient)

    def test_area_code(self):
        self.assertEqual(self.hotel.area_code, self.hotel.address_phone[2:5])

    def test_set_admin_id(self):
        self.hotel.admin_id = None
        self.assertIsNone(self.hotel.admin_id)

        hotel = self.hotel.set_admin_id(self.user)
        self.assertEqual(self.hotel.admin_id, self.user.pk)

    def test_get_admin(self):
        hotel = self.hotel.set_admin_id(self.user)
        self.assertEqual(self.user, self.hotel.get_admin())

    def test_get_admin_none(self):
        self.hotel.admin_id = None
        self.assertIsNone(self.hotel.admin_id)
        self.hotel.save()
        self.assertIsNone(self.hotel.get_admin())

    def test_update_customer(self):
        customer = mommy.make(Customer)
        self.assertIsInstance(customer, Customer)

        hotel = self.hotel.update_customer(customer)
        self.assertEqual(self.hotel.customer, customer)

    def test_update_twilio(self):
        hotel = create_hotel(name='no twilio sid')
        self.assertIsInstance(hotel, Hotel)
        self.assertIsNone(hotel.twilio_sid)
        self.assertIsNone(hotel.twilio_auth_token)

        sid = 'abc'
        hotel = hotel.update_twilio(sid='abc', auth_token='def')
        self.assertIsNotNone(hotel.twilio_sid)
        self.assertIsNotNone(hotel.twilio_auth_token)
        self.assertEqual(hotel.twilio_sid, sid)

    def test_registration_complete(self):
        # Fails b/c existing Hotel doesn't have a Customer
        self.assertFalse(self.hotel.registration_complete)
        # Passes w/ Customer
        customer = mommy.make(Customer)
        self.hotel = self.hotel.update_customer(customer)
        self.assertTrue(self.hotel.registration_complete)

    def test_admin(self):
        self.assertEqual(self.hotel.admin, self.admin)

    def test_redis_key(self):
        self.assertEqual(
            self.hotel.redis_key,
            "{}_{}".format(self.hotel._meta.verbose_name, self.hotel.id)
        )

    def test_redis_sms_count_initial(self):
        cache.delete(self.hotel.redis_key)

        self.assertEqual(self.hotel.redis_sms_count, 0)

    def test_redis_sms_count(self):
        cache.delete(self.hotel.redis_key)

        self.hotel.redis_incr_sms_count()
        
        self.assertEqual(self.hotel.redis_sms_count, 1)

    def test_redis_incr_sms_count_initial(self):
        cache.delete(self.hotel.redis_key)

        self.hotel.redis_incr_sms_count()

        self.assertEqual(cache.get(self.hotel.redis_key), 1)

    def test_redis_incr_sms_count_after_initial(self):
        cache.delete(self.hotel.redis_key)
        
        self.hotel.redis_incr_sms_count()
        self.hotel.redis_incr_sms_count()
        self.hotel.redis_incr_sms_count()

        self.assertEqual(cache.get(self.hotel.redis_key), 3)

    def test_get_or_create_subaccount(self):
        self.hotel.subaccount.delete(override=True)

        with self.assertRaises(Subaccount.DoesNotExist):
            Subaccount.objects.get(hotel=self.hotel)

        make_subaccount(self.hotel, live=True)

        self.hotel.get_or_create_subaccount()
        self.assertIsInstance(self.hotel.subaccount, Subaccount)

    def test_activate(self):
        self.assertTrue(self.hotel.active)
        self.hotel.active = False
        self.hotel.save()
        self.assertFalse(self.hotel.active)

        self.hotel.activate()

        self.assertTrue(self.hotel.active)

    def test_deactivate(self):
        self.assertTrue(self.hotel.active)

        self.hotel.deactivate()

        self.assertFalse(self.hotel.active)
        # reactivate Hotel b/c Live Twilio Subaccount is linked 
        # (even tho account only for test purposes)
        self.hotel.activate()
        

class UserProfileTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.hotel = create_hotel()

    def test_create(self):
        user = mommy.make(User, first_name='Test', last_name='Test')
        user_profile = user.profile
        assert isinstance(user_profile, UserProfile)
        assert str(user_profile) == user_profile.user.username

    def test_delete(self):
        user = mommy.make(User, first_name='Test', last_name='Test')
        user_profiles = UserProfile.objects.all()
        assert len(user_profiles) == 1

        user.delete()
        users = User.objects.all()
        user_profiles = UserProfile.objects.all()
        assert not users
        assert not user_profiles

    def test_manager(self):
        user = mommy.make(User, first_name='Test', last_name='Test')
        user_profiles = UserProfile.objects.all()
        assert len(user_profiles) == 1

        user_profiles = UserProfile.objects.archived()
        assert len(user_profiles) == 0

    def test_is_admin(self):
        admin = create_hotel_user(self.hotel, group='hotel_admin')
        self.assertTrue(admin.profile.is_admin)

    def test_is_manager(self):
        mgr = create_hotel_user(self.hotel, group='hotel_manager')
        self.assertTrue(mgr.profile.is_manager)


class SubaccountTests(TestCase):

    def setUp(self):
        self.password = '1234'
        self.today = timezone.now().date()
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, username='admin', group='hotel_admin')

        self.client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN)

        self.sub = make_subaccount(self.hotel, live=True)

        # Not live
        self.hotel_not_live = create_hotel()
        self.sub_not_live = make_subaccount(self.hotel_not_live)

    ### Manager Tests ###

    def test_twilio_connection(self):
        self.assertIsInstance(self.client, TwilioRestClient)

    def test_get_or_create_already_created(self):
        sub, created = Subaccount.objects.get_or_create(hotel=self.hotel)
        self.assertIsInstance(sub, Subaccount)
        self.assertFalse(created)

    def test_post_save(self):
        self.assertEqual(self.hotel.twilio_sid, self.sub.sid)
        self.assertEqual(self.hotel.twilio_auth_token, self.sub.auth_token)
        self.assertIsInstance(self.hotel._client, TwilioRestClient)

    ### Model Tests

    def test_activate(self):
        self.assertEqual(self.sub.activate(), 'active')

    def test_deactivate(self):
        self.assertEqual(self.sub.deactivate(), 'suspended')
        # set back to "active" b/c this is a live Twilio Subaccount
        self.assertEqual(self.sub.activate(), 'active')
