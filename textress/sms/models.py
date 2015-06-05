from django.db import models
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.timezone import now 
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.utils import IntegrityError
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from twilio import TwilioRestException
from twilio.rest import TwilioRestClient

from sms.helpers import get_weather
from main.models import Hotel, TwilioClient
from utils.exceptions import DailyLimit


#################
# ABSTRACT BASE #
#################

class AbstractBase(models.Model):
    """Abstract model for *created, and modified*."""
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created']


################
# PHONE NUMBER #
################

class PhoneNumberQuerySet(models.query.QuerySet):

    def update_primary(self, hotel, sid):
        "Make sure their are no other Primary PhoneNumbers"
        objs = self.filter(hotel=hotel).exclude(sid=sid)
        for o in objs:
            o.is_primary = False
            o.save()

    def primary(self, hotel):
        try:
            return self.filter(hotel=hotel).get(is_primary=True)
        except ObjectDoesNotExist:
            raise
        except MultipleObjectsReturned:
            self.update_primary(hotel, sid=self.order_by('-created')[0].sid)
            return self.primary(hotel)


class PhoneNumberManager(TwilioClient, models.Manager):

    def get_queryset(self):
        return PhoneNumberQuerySet(self.model, self._db)

    def primary(self, hotel):
        "Return Single Primary PhoneNumber Obj."
        return self.get_queryset().primary(hotel)

    def update_primary(self, hotel, sid):
        "Make sure their are no other Primary PhoneNumbers"
        return self.get_queryset().update_primary(hotel, sid)

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
        try:
            ph_num = self.get(sid=hotel.twilio_ph_sid)
            created = False
        except ObjectDoesNotExist:
            # Buy Twilio Ph#
            number = self.purchase_number(hotel)

            # Assign the Twilio PhoneNumber to the Hotel's Subaccount
            number = self.update_account_sid(hotel, number)

            # Save to DB
            ph_num = self.create(hotel=hotel,
                sid=number.sid,
                phone_number=number.phone_number,
                friendly_name=number.friendly_name)
            created = True

        # assure there is only 1 Primary Ph #
        self.update_primary(hotel=hotel, sid=ph_num.sid)

        return ph_num, created


class PhoneNumber(TwilioClient, AbstractBase):
    # Keys
    hotel = models.ForeignKey(Hotel, related_name="phonenumbers")
    # Fields
    sid = models.CharField(_("Twilio Phone # Sid"), primary_key=True, max_length=50)
    phone_number = models.CharField(_("Twilio Phone #"), max_length=12)
    friendly_name = models.CharField(_("Twilio Friendly Name"), max_length=14, blank=True)
    is_primary = models.BooleanField(_("Is Primary"), blank=True, default=True,
        help_text="only 1 phone number can be the primary")

    objects = PhoneNumberManager()

    def __str__(self):
        return self.friendly_name

    def delete(self, *args, **kwargs):
        # TODO: add HTTP DELETE request here to release Twilio PH #
        try:
            number = self.hotel._client.phone_numbers.get(self.sid)
            number.delete()
        except TwilioRestException as e:
            # TODO: Add logging
            print("{}, {}".format(e.__class__, e))
        return super(PhoneNumber, self).delete(*args, **kwargs)


'''
Denormalize Hotel
-----------------
Twilio PhoneNumber attrs denormalized to Hotel.
'''
@receiver(post_save, sender=PhoneNumber)
def denormalize_twilio_phone(sender, instance=None, created=False, **kwargs):
    if instance.is_primary:
        hotel = instance.hotel
        hotel.twilio_phone_number = instance.phone_number
        hotel.save()