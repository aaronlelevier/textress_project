from django.conf import settings

from twilio.rest import TwilioRestClient

from main.tests.factory import create_hotel
from sms.models import PhoneNumber

# master
# account_sid = settings.TWILIO_ACCOUNT_SID
# auth_token  = settings.TWILIO_AUTH_TOKEN
# client = TwilioRestClient(account_sid, auth_token)
# aaron hotel
account_sid = settings.TWILIO_ACCOUNT_SID_TEST
auth_token  = settings.TWILIO_AUTH_TOKEN_TEST
client = TwilioRestClient(account_sid, auth_token)


def create_phone_number(hotel=None):
    '''Get the first existing Twilio PhoneNumber for the Master 
    Account and create a DB record for it.

    **Note:** Can only get the max real Twilio PH's that exist for 
    the account.
    '''
    count = PhoneNumber.objects.count()
    number = client.phone_numbers.list()[count]
    if not hotel:
        hotel = create_hotel()
    ph_num = PhoneNumber.objects.create(
        hotel=hotel,
        sid=number.sid,
        phone_number=number.phone_number,
        friendly_name=number.friendly_name,
        default=True
    )
    return ph_num