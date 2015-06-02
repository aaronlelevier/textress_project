from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group

from model_mommy import mommy

from main.models import Hotel, Subaccount
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
    'address_phone': '6195105555',
    'address_line1': '123 Some St.',
    'address_city': 'San Diego',
    'address_state': STATES[0][0],
    'address_zip': '92131'
    }

PASSWORD = '1234'


def create_hotel(name="Test"):
    address_data = CREATE_HOTEL_DICT
    address_data['name'] = name
    return Hotel.objects.create(**address_data)


def create_hotel_user(hotel, username='user'):
    '''
    Default Hotel User with no Admin or Manager permissions.

    :hotel: Hotel Object
    '''
    user = mommy.make(User, username=username, password=PASSWORD)
    user.set_password("1234")
    user.save()
    user.profile.update_hotel(hotel)
    return User.objects.get(username=username)


def create_hotel_manager(hotel, username='manager'):
    '''
    Default Hotel User with no Admin or Manager permissions.

    :hotel: Hotel Object
    '''
    user = mommy.make(User, username=username, password=PASSWORD)
    manager_group = Group.objects.get(name="hotel_manager")
    user.groups.add(manager_group)
    user.set_password("1234")
    user.save()
    user.profile.update_hotel(hotel)
    return User.objects.get(username=username)


def make_subaccount(hotel, live=False):
    '''
    If not "live", override Subaccount.save() so don't create a 
    live Twilio Subaccount.
    '''
    global Subaccount
    
    if live:
        return Subaccount.objects.create(hotel=hotel)
    else:
        Subaccount.save = models.Model.save
        return mommy.make(Subaccount, hotel=hotel)