from django.db import models

from model_mommy import mommy

from ..models import Hotel, Subaccount

from utils.data import STATES


def create_hotel(name="Test"):
    address_data = {
        'address_phone': '7025105555',
        'address_line1': '123 Some St.',
        'address_city': 'San Diego',
        'address_state': STATES[0][0],
        'address_zip': '92131',
        'rooms': 500
        }
    address_data['name'] = name
    return Hotel.objects.create(**address_data)


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