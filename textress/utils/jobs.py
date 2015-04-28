'''
Standard Jobs that will run via a `Service Broker`
'''
from sms.models import PhoneNumber

def denormalize_phone_numbers():
    for ph in PhoneNumber.objects.filter(is_primary=True):
        hotel = ph.hotel
        hotel.address_phone = ph.phone_number
        hotel.save()