import os
from mock import patch
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
    make_subaccount, make_subaccount_live)
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

        self.sub = make_subaccount_live(self.hotel)

        # AcctTrans, TransType, etc...
        self.sms_used, _ = TransType.objects.get_or_create(name='sms_used')
        # Guest
        self.guest = make_guests(hotel=self.hotel, number=1)[0] #b/c returns a list
        # Messages
        self.messages = make_messages(
            insert_date=timezone.localtime(timezone.now()).date(),
            hotel=self.hotel,
            user=self.admin,
            guest=self.guest
        )

        # Hotel2
        self.hotel2 = create_hotel()

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

    # redis_sms_count

    def test_redis_sms_count__initial(self):
        cache.delete(self.hotel.redis_key)

        self.assertEqual(self.hotel.redis_sms_count, 0)

    def test_redis_sms_count(self):
        cache.delete(self.hotel.redis_key)

        self.hotel.redis_incr_sms_count()
        
        self.assertEqual(self.hotel.redis_sms_count, 1)

    # redis_incr_sms_count

    def test_redis_incr_sms_count__initial(self):
        cache.delete(self.hotel.redis_key)

        self.hotel.redis_incr_sms_count()

        self.assertEqual(cache.get(self.hotel.redis_key), 1)

    def test_redis_incr_sms_count__after_initial(self):
        cache.delete(self.hotel.redis_key)
        
        self.hotel.redis_incr_sms_count()
        self.hotel.redis_incr_sms_count()
        self.hotel.redis_incr_sms_count()

        self.assertEqual(cache.get(self.hotel.redis_key), 3)

    @patch("account.models.AcctTransManager.check_balance")
    def test_redis_incr_sms_count__finally(self, check_balance_mock):
        """
        Will call 'check_balance' and 'reset_count' if necessary when triggered.
        """
        cache.set(self.hotel.redis_key, settings.CHECK_SMS_LIMIT)

        self.hotel.redis_incr_sms_count()

        self.assertTrue(check_balance_mock.called)
        self.assertEqual(self.hotel.redis_sms_count, 0)

    # check_sms_count

    def test_check_sms_count__sms_count_less_than_limit(self):
        cache.set(self.hotel.redis_key, settings.CHECK_SMS_LIMIT-1)

        self.hotel.check_sms_count()

        self.assertEqual(self.hotel.redis_sms_count, settings.CHECK_SMS_LIMIT-1)

    @patch("account.models.AcctTransManager.check_balance")
    def test_check_sms_count__trigger(self, check_balance_mock):
        cache.set(self.hotel.redis_key, settings.CHECK_SMS_LIMIT)

        self.hotel.check_sms_count()

        self.assertTrue(check_balance_mock.called)
        self.assertEqual(self.hotel.redis_sms_count, 0)

    # get_subaccount

    def test_get_subaccount(self):
        sub = make_subaccount(self.hotel2)

        self.assertEqual(
            self.hotel2.get_subaccount(),
            self.hotel2.subaccount
        )

    def test_get_subaccount__none(self):
        self.assertIsNone(self.hotel2.get_subaccount())

    # get_or_create_subaccount

    def test_get_or_create_subaccount(self):
        self.hotel.subaccount.delete(override=True)

        with self.assertRaises(Subaccount.DoesNotExist):
            Subaccount.objects.get(hotel=self.hotel)

        make_subaccount_live(self.hotel)

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
        self.assertIsInstance(user_profile, UserProfile)
        self.assertEqual(str(user_profile), user_profile.user.username)

    def test_delete(self):
        user = mommy.make(User, first_name='Test', last_name='Test')
        user_profiles = UserProfile.objects.all()
        self.assertEqual(len(user_profiles), 1)

        user.delete()
        users = User.objects.all()
        user_profiles = UserProfile.objects.all()
        self.assertFalse(users)
        self.assertFalse(user_profiles)

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

    # hotel_group

    def test_hotel_group__admin(self):
        group_name = 'hotel_admin'
        admin = create_hotel_user(self.hotel, group=group_name)

        ret = admin.profile.hotel_group()

        self.assertEqual(ret, Hotel.group_names_dict()[group_name])

    def test_hotel_group__manager(self):
        group_name = 'hotel_manager'
        manager = create_hotel_user(self.hotel, group=group_name)

        ret = manager.profile.hotel_group()

        self.assertEqual(ret, Hotel.group_names_dict()[group_name])

    def test_hotel_group__user(self):
        user = create_hotel_user(self.hotel)

        ret = user.profile.hotel_group()

        self.assertEqual(ret, '')


class SubaccountTests(TestCase):

    def setUp(self):
        self.password = '1234'
        self.today = timezone.localtime(timezone.now()).date()
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, username='admin', group='hotel_admin')

        self.client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN)

        self.sub = make_subaccount_live(self.hotel)

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

    def test_model_fields(self):
        self.assertEqual(self.sub.hotel, self.hotel)
        self.assertIsNotNone(self.sub.sid)
        self.assertIsNotNone(self.sub.auth_token)
        self.assertTrue(self.sub.active)

    def test_activate(self):
        self.sub.active = False
        self.sub.save()
        self.assertFalse(self.sub.active)

        ret = self.sub.activate()

        self.assertEqual(ret, 'active')
        self.assertTrue(self.sub.active)

    def test_deactivate(self):
        self.assertTrue(self.sub.active)

        ret = self.sub.deactivate()

        self.assertEqual(ret, 'suspended')
        self.assertFalse(self.sub.active)

        # set back to "active" b/c this is a live Twilio Subaccount
        self.assertEqual(self.sub.activate(), 'active')
