from django.conf import settings
from django.contrib.auth.models import User

from twilio import TwilioRestException
from twilio.rest import TwilioRestClient

# Global Auth Tokens for Twilio REST
account_sid = settings.TWILIO_ACCOUNT_SID
auth_token = settings.TWILIO_AUTH_TOKEN



class TwilioHotel(object):
    """
    New Hotel Signup Proces
    ----------------------

    1. New Hotel Signs Up
        - self.hotel is a main.models.Hotel object

    2. Create a New SubAccount
        - friendly_name == Hotel.name
        - returns: account
        - account.sid = Message.account_sid

    3. Link credentials of SubAccount to the New Hotel
        - Manager method to handle linking Subaccount_sid to UserProfile

    4. Create New PhoneNumber for New Hotel
        - Returns: "number"
        - Important properties:
            'phone_number': '+17029196092',
            'capabilities': {'SMS': True, 'voice': True, 'MMS': True}
        - 2 Steps -
            A: Find available PhoneNumber using "AvailablePhoneNumbers" resource
            B: POST to "IncomingPhoneNumbers" resource
                1. Get PhoneNumber that was just bought
                2. Add it to SubAccount

    # TODO 5. Place a Call or Text to New Hotel to confirm Human via the New PhoneNumber

    """

    def __init__(self, hotel, account_sid=settings.TWILIO_ACCOUNT_SID,
        auth_token=settings.TWILIO_AUTH_TOKEN, *args, **kwargs):

        self.client = TwilioRestClient(account_sid, auth_token)
        self.hotel = hotel

    def get_subaccount(self):
        """ Returns Twilio Subaccount Object. """
        try:
            subaccount = self.client.accounts.get(self.hotel.subaccount_sid)
        except TwilioRestException:
            subaccount = self.client.accounts.create(friendly_name=self.hotel.name)
        return subaccount

    @property
    def subaccount_sid(self):
        return self.get_subaccount().sid

    @property
    def phone_number(self):
        """
        Return the PhoneNumber Twilio Object. Purchased phone_numbers have a 'sid'.
        kwargs:
            area_code: 3 digit area_code
            contains: any phone numbers or letters wanted in the phone #.
            ex: contains="510555****" or contains="STORM"
        """
        try:
            return self.client.phone_numbers.get(self.hotel.phone_number_sid)
        except TwilioRestException:
            raise

    def available_phone_numbers(self, limit=10):
        """Get next (default `limit=10`) available phone numbers based
            on `area_code` of the Hotel."""
        numbers = self.client.phone_numbers.search(
            area_code=self.hotel.area_code, sms_enabled=True,
            voice_enabled=True, mms_enabled=True)
        return numbers[:limit]

    def transfer_phone_number(self):
        try:
            number = self.client.phone_numbers.update(
                self.phone_number.sid, account_sid=self.hotel.account_sid)
        except TwilioRestException as e:
            raise e("Check phone_number.sid: {}\nAnd account_sid: {}\nTransfer \
                failed.".format(self.phone_number.sid, self.hotel.account_sid))



"""
Useful functions
"""
def update_phone_number(phone_number, voice_url, phone_url):
    """
    Use to update 'receive_sms url for ex'.
    voice_url / phone_url : are fully qualified URLs
    """
    return client.phone_numbers.update(phone_number.sid,
        voice_url=voice_url, phone_url=phone_url)

def list_phone_numbers():
    numbers = client.phone_numbers.list()
    return [n.phone_number for n in numbers]

def update_account(account_sid, auth_token, **kwargs):
    """Possible update kwargs would be `status`, voice_url, sms_url."""
    client = TwilioRestClient(account_sid, auth_token)
    return client.accounts.update(account_sid, **kwargs)