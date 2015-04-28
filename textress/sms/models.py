from django.db import models
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.utils.timezone import now 
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import IntegrityError
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete

from twilio import TwilioRestException
from twilio.rest import TwilioRestClient

from .helpers import get_weather
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


########
# TEXT #
########

class TextManager(models.Manager):

    def sent(self):
        return self.filter(sent=True)

    def not_sent(self):
        return self.filter(sent=False)


class Text(models.Model):
    """
    Twilio SMS info to send. Default to my ph # for testing, and
    Yahoo! Weather API - for default test messages.
    """
    created = models.DateTimeField(auto_now_add=True)
    to = models.CharField(_("To"), max_length=12)
    frm = models.CharField(_("From"), max_length=12, blank=True, default=settings.PHONE_NUMBER)
    body = models.CharField(_("Body"), max_length=160, blank=True)
    sent = models.BooleanField(_("Sent"), blank=True, default=True)

    objects = TextManager()

    def __str__(self):
        return self.body

    def save(self, *args, **kwargs):
        if not self.body: 
            self.body = get_weather()
        super().save(*args, **kwargs)


##############
# DEMO COUNTER
##############

class DemoCounterQuerySet(models.query.QuerySet):
    def today(self):
        return self.get(day=now())


class DemoCounterManager(models.Manager):
    '''
    Goal: To manage that the # of Demo Texts don't go over the Daily Limit.
    '''
    def get_queryset(self):
        return DemoCounterQuerySet(self.model, self._db)

    def delete_all(self):
        return [ea.delete() for ea in self.all()]
        
    def today(self):
        try:
            return self.get_queryset().today()
        except ObjectDoesNotExist as e:
            raise e

    def create_count(self, *args, **kwargs):
        # get obj or create new one
        try:
            cur_count = self.get_queryset().today()
        except ObjectDoesNotExist:
            return self.create()
        else:
            # if get() succeeds: raise error if limit reached, else: increment count
            try:
                cur_count.count += 1
                cur_count.save()
                return cur_count
            except DailyLimit as e:
                raise e
        

class DemoCounter(models.Model):
    """
    Limit Demo texts sent daily to 50x per day.
    Called in clean() method of DemoForm.
    """
    day = models.DateField(_("Day"), primary_key=True, auto_now_add=True)
    count = models.IntegerField(_("Daily Count"), default=1, blank=True)

    objects = DemoCounterManager()

    def __str__(self):
        return "{0}: {1}".format(self.day, self.count)

    def save(self, *args, **kwargs):
        self.check_limit()
        super().save(*args, **kwargs)

    def check_limit(self):
        if self.count > settings.SMS_LIMIT:
            raise DailyLimit

################
# PHONE NUMBER #
################

class PhoneNumberQuerySet(models.query.QuerySet):

    def primary(self):
        try:
            return self.get(is_primary=True)
        except ObjectDoesNotExist:
            raise 

class PhoneNumberManager(TwilioClient, models.Manager):

    def get_queryset(self):
        return PhoneNumberQuerySet(self.model, self._db)

    def primary(self):
        "Return Single Primary PhoneNumber Obj."
        return self.get_queryset().primary()

    def update_primary(self, hotel, sid):
        "Make sure their are no other Primary PhoneNumbers"
        objs = self.filter(hotel=hotel).exclude(sid=sid)
        for o in objs:
            o.is_primary = False
            o.save()

    def purchase_number(self, hotel):
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
            db_number = self.get(sid=hotel.twilio_ph_sid)
            created = False
        except ObjectDoesNotExist:
            # Buy Twilio Ph#
            number = self.purchase_number(hotel)

            # Assign the Twilio PhoneNumber to the Hotel's Subaccount
            number = self.update_account_sid(hotel, number)

            # Save to DB
            db_number = self.create(hotel=hotel,
                sid=number.sid,
                phone_number=number.phone_number,
                friendly_name=number.friendly_name)
            created = True

        # assure there is only 1 Primary Ph #
        self.update_primary(hotel=hotel, sid=db_number.sid)

        return db_number, created


class PhoneNumber(TwilioClient, AbstractBase):
    # Keys
    hotel = models.ForeignKey(Hotel, related_name="phone_number")
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
        return super().delete(*args, **kwargs)


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