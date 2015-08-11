from django.db import models
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.timezone import now 
from django.core.exceptions import (ObjectDoesNotExist, MultipleObjectsReturned,
    ValidationError)
from django.db.utils import IntegrityError
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from twilio import TwilioRestException
from twilio.rest import TwilioRestClient

from sms.helpers import get_weather
from main.models import Hotel, TwilioClient
from utils.exceptions import DailyLimit
from utils.models import TimeStampBaseModel


################
# PHONE NUMBER #
################

class PhoneNumberQuerySet(models.query.QuerySet):

    def default(self, hotel):
        '''
        Returns the single "default" PhoneNumber object default.
        '''
        try:
            return self.get(hotel=hotel, default=True)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return []


class PhoneNumberManager(TwilioClient, models.Manager):

    def get_queryset(self):
        return PhoneNumberQuerySet(self.model, self._db)

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
        "Public method for setting a PhoneNumber to the Default."
        self._validate_ph_num(hotel, sid)
        self._set_default(hotel, sid)
        self._update_non_defaults(hotel, sid)

    def default(self, hotel):
        '''
        Returns the single "default" PhoneNumber object.
        defaul
        '''
        return self.get_queryset().default(hotel)

    ### TWILIO

    def purchase_number(self, hotel):
        "Based on ``area_code`` of the Hotel."
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
        Assings PH # to Hotel.
        Denormalize Twilio PH # Fields
        Return: Twilio PhoneNumber Object.
        '''
        number = self.client.phone_numbers.update(
            number.sid, account_sid=hotel.twilio_sid)

        hotel.update_twilio_phone(ph_sid=number.sid,
            phone_number=number.phone_number)

        return number

    def get_or_create(self, hotel, *args, **kwargs):
        '''
        Standard ``.get_or_create()`` but if a Create is called, the 
        PhoneNumber will be purchased from Twilio and set as the default.
        '''
        try:
            ph = self.get(sid=hotel.twilio_ph_sid)
            created = False
        except ObjectDoesNotExist:
            # Buy Twilio Ph#
            number = self.purchase_number(hotel)
            # Assign the Twilio PhoneNumber to the Hotel's Subaccount
            number = self.update_account_sid(hotel, number)
            # Save to DB
            ph = self.create(hotel=hotel,
                sid=number.sid,
                phone_number=number.phone_number,
                friendly_name=number.friendly_name)
            created = True
        # assure there is only 1 Primary Ph #
        self.update_default(hotel=hotel, sid=ph.sid)
        return ph, created


class PhoneNumber(TwilioClient, TimeStampBaseModel):
    '''
    All "phone number" fields should be stored as "+18001234567" i.e. +1\d{10} 
    and should only be "friendly" formatted only when rendered in the template.
    '''
    # Keys
    hotel = models.ForeignKey(Hotel, related_name="phonenumbers")
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

    def delete(self, *args, **kwargs):
        # TODO: Verify this delete actually deletes the PH
        try:
            number = self.hotel._client.phone_numbers.get(self.sid)
            number.delete()
        except TwilioRestException as e:
            # TODO: Add logging
            raise("{}, {}".format(e.__class__, e))
        return super(PhoneNumber, self).delete(*args, **kwargs)


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
