import os
import random
from twilio.rest import TwilioRestClient

from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.utils import timezone

from model_mommy import mommy

from .factory import create_hotel

from ..models import Hotel, UserProfile, Subaccount

from utils import create
from payment.models import Customer
from utils.data import STATES


class HotelTests(TestCase):

    fixtures = ['main.json']

    def setUp(self):
        self.password = '1234'
        self.hotel = create_hotel()
        self.dave_hotel = Hotel.objects.get(name='Dave Hotel')

        self.user = User.objects.create_user('Test', settings.DEFAULT_FROM_EMAIL, self.password)
        self.user.set_password(self.password)
        self.user.save()
        self.user_profile = self.user.profile
        self.user_profile.update_hotel(self.dave_hotel)

    def test_create(self):
        assert isinstance(self.hotel, Hotel)
        assert isinstance(self.dave_hotel, Hotel)
        assert isinstance(self.user, User)

    def test_twilio_client(self):
        assert isinstance(self.dave_hotel._client, TwilioRestClient)

    def test_area_code(self):
        assert self.hotel.area_code == '702'

    def test_clean_phone(self):
        clean_phone = self.hotel._clean_phone(self.hotel.address_phone)
        assert clean_phone == self.hotel.address_phone

    def test_get_absolute_url(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(self.dave_hotel.get_absolute_url())
        assert response.status_code == 200

    def test_set_admin_id(self):
        self.hotel.admin_id = None
        assert not self.hotel.admin_id

        hotel = self.hotel.set_admin_id(self.user)
        assert self.hotel.admin_id == self.user.pk

    def test_update_customer(self):
        customer = mommy.make(Customer)
        assert isinstance(customer, Customer)

        hotel = self.hotel.update_customer(customer)
        assert self.hotel.customer == customer

    def test_update_twilio(self):
        hotel = create_hotel(name='no twilio sid')
        assert isinstance(hotel, Hotel)
        assert not hotel.twilio_sid
        assert not hotel.twilio_auth_token

        hotel.update_twilio(sid='abc', auth_token='def')
        assert hotel.twilio_sid
        assert hotel.twilio_auth_token

    def test_is_textress(self):
        textress = create_hotel('Textress Hotel')
        assert textress.is_textress
        

class UserProfileTests(TestCase):

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


class SubaccountTests(TestCase):

    def setUp(self):
        self.password = '1234'
        self.today = timezone.now().date()

        # Twilio Test Sid
        # name='sub_test_865'
        self.test_sid = os.environ['TWILIO_ACCOUNT_SID_TEST']
        self.test_auth_token = os.environ['TWILIO_AUTH_TOKEN_TEST']

        # Hotel
        randint = random.randint(0,1000)
        self.hotel = create_hotel(name="sub_test_{}".format(randint))

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

        self.client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN)

    ### Manager Tests ###

    def test_twilio_connection(self):
        assert isinstance(self.client, TwilioRestClient)

    def test_get(self):
        hotel = create_hotel(name='sub_test_865')

        # Get
        sub = Subaccount.objects.create(
            hotel=hotel,
            sid=self.test_sid,
            auth_token=self.test_auth_token)
        assert isinstance(sub, Subaccount)

        sub_2, created = Subaccount.objects.get_or_create(hotel=hotel)
        assert not created
        assert sub == sub_2

        # the DB instance is created, but the Twilio Instance is not
        assert len(self.client.accounts.list(friendly_name=hotel.name)) == 2

    # # Commented out b/c makes a live Twilio Subaccount ea. time
    # def test_twilio_create_create(self):
    #     # Create Subaccount
    #     sub, created = Subaccount.objects.get_or_create(self.hotel)
    #     assert isinstance(sub, Subaccount)
    #     assert created
    #     assert len(self.client.accounts.list(friendly_name=self.hotel.name)) == 1

    #     # indempotent
    #     sub, created = Subaccount.objects.get_or_create(self.hotel)
    #     assert isinstance(sub, Subaccount)
    #     assert not created
    #     assert len(self.client.accounts.list(friendly_name=self.hotel.name)) == 1


    ### Model Tests ###










