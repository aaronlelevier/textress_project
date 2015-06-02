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


def create_hotel_user(hotel_name=CREATE_HOTEL_DICT['name']):
    '''
    Default Hotel User with no Admin or Manager permissions.
    '''
    hotel = Hotel.objects.get(name=hotel_name)
    user = mommy.make(User, username='user', password=PASSWORD)
    return user.profile.update_hotel(hotel)


def create_hotel_manager(hotel_name=CREATE_HOTEL_DICT['name']):
    '''
    Default Hotel User with no Admin or Manager permissions.
    '''
    hotel = Hotel.objects.get(name=hotel_name)
    user = mommy.make(User, username='manager', password=PASSWORD)
    manager_group = Group.objects.get(name="hotel_manager")
    user.groups.add(manager_group)
    user.save()
    return user.profile.update_hotel(hotel)


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