import sys

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.exceptions import (ObjectDoesNotExist, MultipleObjectsReturned,
    ValidationError)
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from twilio import TwilioRestException

from account.models import AcctTrans, TransType
from main.models import Hotel, TwilioClient
from utils import email
from utils.exceptions import PhoneNumberNotDeletedExcp
from utils.models import TimeStampBaseModel


################
# PHONE NUMBER #
################

class PhoneNumberManager(TwilioClient, models.Manager):

    ### UPDATE PRIMARY

    def _validate_ph_num(self, hotel, sid):
        "The PhoneNumber exists for the Hotel."
        try:
            ph = self.get(hotel=hotel, sid=sid)
        except PhoneNumber.DoesNotExist:
            raise ValidationError("The PhoneNumber does not exist for \
hotel: {}".format(hotel))
        return ph

    def _set_default(self, hotel, sid):
        """Set the Default Card before calling the complete 
        ``update_default`` method."""
        ph = self.get(sid=sid)
        ph.default = True
        ph.save()
        return ph

    def _update_non_defaults(self, hotel, sid):
        "All other 'non-default' PhoneNumbers are set as default=False."
        for ph in self.filter(hotel=hotel, default=True).exclude(sid=sid):
            ph.default = False
            ph.save()

    def update_default(self, hotel, sid):
        """
        Call all set default PH logic.

        :hotel: Hotel object
        :sid: PhoneNumber.sid that will be set as the **default**
        """
        self._validate_ph_num(hotel, sid)
        ph = self._set_default(hotel, sid)
        hotel.update_twilio_phone(ph.sid, ph.phone_number)
        self._update_non_defaults(hotel, sid)
        return ph

    def default(self, hotel):
        '''
        Returns the single "default" PhoneNumber object default.
        '''
        ph_nums = self.filter(hotel=hotel)
        if not ph_nums:
            return []
        else:
            try:
                return ph_nums.get(default=True)
            except (ObjectDoesNotExist, MultipleObjectsReturned):
                ph = ph_nums[0]
                ph = self.update_default(hotel, ph.sid)
                return ph

    ### TWILIO

    def _twilio_purchase_number(self, hotel):
        """
        Purchase live Twilio PH # based on ``area_code`` of the Hotel.
        """
        if 'test' not in sys.argv:
            number = None
            while not number:
                numbers = self.client.phone_numbers.search(
                    area_code=hotel.area_code, sms_enabled=True,
                    voice_enabled=True, mms_enabled=True)
                if numbers:
                    number = numbers[0].purchase()
            return number

    def update_account_sid(self, hotel, number):
        '''
        Transfer on Twilio the PhoneNumber to the Hotel's 
        Subaccount.

        Update denormalized PH fields on Hotel.

        :hotel: Hotel object
        :number: PhoneNumber object
        '''
        number = self.client.phone_numbers.update(number.sid,
            account_sid=hotel.twilio_sid,
            sms_url="https://textress.com/api/receive/sms_url/")

        hotel.update_twilio_phone(ph_sid=number.sid,
            phone_number=number.phone_number)

    def create_from_twilio(self, hotel, twilio_ph):
        """Using a Twilio PH obj, create a DB record, and transfer 
        the PH to the Hotel's Subaccount w/i Twilio."""

        # DB create
        number = self.create(hotel=hotel,
            sid=twilio_ph.sid,
            phone_number=twilio_ph.phone_number,
            friendly_name=twilio_ph.friendly_name)

        # Xfr Twilio PH to Hotel Subaccount
        self.update_account_sid(hotel, number)

        return number

    def purchase_number(self, hotel):
        '''
        Calls all logic for the Purchase of a New PhoneNumber.
        '''
        # LIVE: Twilio PH Num purchase
        twilio_ph = self._twilio_purchase_number(hotel)
        
        # LIVE: Stripe Charge
        acct_tran = AcctTrans.objects.phone_number_charge(hotel,
            phone_number=twilio_ph.phone_number)

        # DB create (but LIVE updates my current Twilio PH Num REST API 
        # endpoint for the PH Num)
        number = self.create_from_twilio(hotel, twilio_ph)

        # Update default
        self.update_default(hotel, number.sid)
        
        return number

    def get_or_create(self, hotel, *args, **kwargs):
        '''
        Standard ``.get_or_create()`` but if a Create is called, the 
        PhoneNumber will be purchased from Twilio and set as the default.
        '''
        try:
            ph = self.get(hotel=hotel, default=True)
            created = False
        except ObjectDoesNotExist:
            ph = self.purchase_number(hotel)
            created = True

        # assure there is only 1 Primary Ph #
        self.update_default(hotel=hotel, sid=ph.sid)
        
        return ph, created

    def delete_unknown_number(self, ph_num):
        """
        Delete the PH in the DB and Twilio, or send an email to myself, if 
        I need to manually delete it.

        :ph_num: the twilio formatted string of the PH. (ex: +17025551234)
        """
        # Check if PH exists on the Master Account
        try:
            ph = PhoneNumber.objects.get(phone_number=ph_num)
        except PhoneNumber.DoesNotExist:
            email.send_delete_unknown_number_failed_email(ph_num)
        else:
            try:
                self.client.phone_numbers.get(ph.sid).delete()
            except TwilioRestException:
                email.send_delete_unknown_number_failed_email(ph_num)


class PhoneNumber(TwilioClient, TimeStampBaseModel):
    '''
    All "phone number" fields should be stored as "+18001234567" i.e. +1\d{10} 
    and should only be "friendly" formatted only when rendered in the template.
    '''
    # Keys
    hotel = models.ForeignKey(Hotel, related_name="phone_numbers")
    # Fields
    sid = models.CharField(_("Twilio Phone # Sid"), primary_key=True, max_length=50)
    phone_number = models.CharField(_("Twilio Phone #"), max_length=12)
    friendly_name = models.CharField(_("Twilio Friendly Name"), max_length=14, blank=True)
    default = models.BooleanField(_("Is Primary"), blank=True, default=True,
        help_text="only 1 phone number can be the primary")

    objects = PhoneNumberManager()

    def __str__(self):
        return self.friendly_name

    def save(self, *args, **kwargs):
        if self.default:
            PhoneNumber.objects._update_non_defaults(self.hotel, self.sid)
        return super(PhoneNumber, self).save(*args, **kwargs)

    def delete(self):
        # Twilio Delete
        try:
            number = self.hotel._client.phone_numbers.get(self.sid)
            number.delete()
        except TwilioRestException:
            raise PhoneNumberNotDeletedExcp()

        # Remove denormalized PH reference on Hotel
        self.hotel.remove_twilio_phone()

        # DB PhoneNumber delete
        return super(PhoneNumber, self).delete()

    @property
    def monthly_charge_desc(self):
        return "monthly charge: {}".format(self.phone_number)


'''
Denormalize Hotel
-----------------
Twilio PhoneNumber attrs denormalized to Hotel.

The ``hotel.twilio_phone_number`` is the default Twilio PhoneNumber in use.
'''
@receiver(post_save, sender=PhoneNumber)
def denormalize_twilio_phone(sender, instance=None, created=False, **kwargs):
    if instance.default:
        hotel = instance.hotel
        hotel.twilio_phone_number = instance.phone_number
        hotel.save()