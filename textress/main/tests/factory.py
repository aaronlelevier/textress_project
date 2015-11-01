from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group

from model_mommy import mommy
from twilio.rest import TwilioRestClient

from main.models import Hotel, Subaccount
from utils import create
from utils.data import STATES


CREATE_USER_DICT = {
    'username': 'test',
    'first_name': 'Test',
    'last_name': 'Test',
    'email':settings.DEFAULT_FROM_EMAIL,
    'password1': '1234',
    'password2': '1234'
    }

CREATE_HOTEL_DICT = {
    'name': 'Test Hotel',
    'address_phone': create._generate_ph(),
    'address_line1': '123 Some St.',
    'address_city': 'San Diego',
    'address_state': STATES[0][0],
    'address_zip': '92131',
    'twilio_phone_number': create._generate_ph()
    }

PASSWORD = '1234'


def create_hotel(name=None, address_phone=None):
    '''
    Standard test Hotel.
    '''
    address_data = CREATE_HOTEL_DICT
    if not name:
        name = create._generate_name()
    address_data['name'] = name

    if not address_phone:
        address_data['address_phone'] = create._generate_ph()
    address_data['address_phone']

    return Hotel.objects.create(**address_data)


def create_hotel_user(hotel, username=None, group=None):
    '''Handle making Admin, Manager, and Users with 1 Func.'''
    
    if not username:
        username = create._generate_name()

    user, group = create_user(username, group)

    # if this is not done, ``main.mixins.AdminOnlyMixin`` will raise a 404
    if group and group.name == 'hotel_admin':
        hotel.set_admin_id(user)

    user.profile.update_hotel(hotel)

    return user


def create_user(username=create._generate_name(), group=None):
    """Create a User w/o a Hotel"""

    user = mommy.make(User, username=username, password=PASSWORD,
        first_name=username, last_name=username, email="{}@mail.com".format(username))
    user.set_password(PASSWORD)
    user.save()

    if group:
        group = Group.objects.get(name=group)
        user.groups.add(group)

    return user, group

    
def create_superuser():
    hotel = create_hotel(address_phone='7754194000')
    superuser = create_hotel_user(hotel, username='admin')


def make_subaccount(hotel, live=False):
    '''
    TODO
    ----
    Find out how to incorporate this method because not currently being used.

    If not "live", override Subaccount.save() so don't create a 
    live Twilio Subaccount.
    '''
    if live:
        client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN)

        subaccount = client.accounts.list()[0]

        return Subaccount.objects.create(
            hotel=hotel,
            sid=subaccount.sid,
            auth_token=subaccount.auth_token)
    else:
        global Subaccount
        Subaccount.save = models.Model.save
        return mommy.make(Subaccount, hotel=hotel)