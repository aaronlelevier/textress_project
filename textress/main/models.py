import re
import random
import string

from django.db import models
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User, Group
from django.utils.text import slugify
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.forms.models import model_to_dict

from twilio import TwilioRestException
from twilio.rest import TwilioRestClient
from rest_framework.authtoken.models import Token

from payment.models import Customer
from utils import validate_phone, dj_messages, exceptions as excp
from utils.data import STATES, HOTEL_TYPES
from utils.models import AbstractBase



def viewable_user_fields_dict(user):
    "A ``Dict`` of all viewable ``User` fields to be displayed in templates."
    user_dict = {}
    for k,v in model_to_dict(user).iteritems():
        if k in ['username', 'first_name', 'last_name', 'is_active', 'email']:
            user_dict.update({k:v})
    return user_dict


class TwilioClient(object):

    def __init__(self, *args, **kwargs):
        super(TwilioClient, self).__init__(*args, **kwargs)

        # bring in Twilio and get API key from settings.py
        self.client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN)


#########
# HOTEL #
#########

class HotelQuerySet(models.query.QuerySet):
    pass


class HotelManager(models.Manager):

    def get_queryset(self):
        return HotelQuerySet(self.model, self._db)

    def textress(self):
        return self.get(name=settings.TEXTRESS_HOTEL)

    def get_by_phone(self, ph_num):
        '''
        TODO
        ----
        If `HotelPhoneNotFound` is triggered, I have a live Twilio
        PhoneNumber that is not assigned to a Hotel, and needs to be
        removed.
        '''
        try:
            return self.get(twilio_phone_number=ph_num)
        except ObjectDoesNotExist:
            # TODO: Change to a Celery request to delete the `PhoneNumber`
            # method: PhoneNumber.objects.delete(phone_number=address_phone)
            return self.get(name=settings.TEXTRESS_HOTEL)
          

class Hotel(TwilioClient, AbstractBase):
    """
    `customer` ForeignKey is the entry point p/ Hotel to Stipe.

    Denormalized Fields: twilio_sid, twilio_auth_token, phone_number(primary)
        Expl: for speed, so don't have to always access these models, and because
        there are multiple `phone_numbers` so know which one is the "primary"
    """
    # Required
    name = models.CharField(_("Hotel Name"), unique=True, max_length=100)
    address_phone = models.CharField(_("Contact Phone Number"), unique=True, max_length=12,
        help_text="10-digit phone number. i.e.: 7025101234")
    address_line1 = models.CharField(_("Address Line 1"), max_length=100)
    address_city = models.CharField(_("City"), max_length=100)
    address_state = models.CharField(_("State"), max_length=25, choices=STATES, default=STATES[0][0])
    address_zip = models.PositiveIntegerField(_("Zipcode"), help_text="5-digit zipcode. i.e.: 89109")
    # Optional
    address_line2 = models.CharField(_("Address Line 2"), max_length=100, blank=True)
    hotel_type = models.CharField(_("Hotel Type"), max_length=100, choices=HOTEL_TYPES,
        default='', blank=True)
    rooms = models.IntegerField(_("Rooms"), blank=True, null=True)
    # Auto
    slug = models.SlugField(_("Slug"), max_length=125, unique=True, blank=True)
    active = models.BooleanField(blank=True, default=True,
        help_text="Deactivate Hotel here when they run out of funds to send SMS.")
    group_name = models.CharField(blank=True, max_length=100)
    # Stripe
    customer = models.ForeignKey(Customer, blank=True, null=True,
        help_text="Stripe Customer Id")
    admin_id = models.IntegerField(_("Hotel Admin ID"),unique=True, blank=True, null=True,
        help_text="1 Hotel Admin User per Hotel")
    # Denormalized Fields
    twilio_sid = models.CharField(_("Twilio Sid"), max_length=100, blank=True, null=True)
    twilio_auth_token = models.CharField(_("Twilio Auth Token"), max_length=100, blank=True, null=True)
    twilio_phone_number = models.CharField(_("Twilio Phone Number"), max_length=25, blank=True, null=True)
    twilio_ph_sid = models.CharField(_("Twilio Phone Number Sid"), max_length=100, blank=True, null=True)

    objects = HotelManager()

    def __str__(self):
        return self.name

    @property
    def _client(self):
        try:
            return TwilioRestClient(self.twilio_sid, self.twilio_auth_token)
        except TwilioRestException:
            # TODO: Add logging or forms.ValidationError here?
            raise

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)

        # Hotel Group [Anonymous Group name to be used w/ ``ws4redis`` Group Messaging]
        self.group_name = self.slug + '_' + ''.join([str(random.choice(string.digits)) for x in range(10)])
        g, created = Group.objects.get_or_create(name=self.group_name)

        # Always use Twilio phone formatting
        if self.address_phone:
            self.address_phone = validate_phone(self.address_phone)

        return super(Hotel, self).save(*args, **kwargs)

    @property
    def area_code(self):
        return self.address_phone[2:5]

    @property
    def is_textress(self):
        return self.name == settings.TEXTRESS_HOTEL

    @property
    def registration_complete(self):
        '''
        A valid ``Customer``(Stripe) means the Admin User payed during Registration. 
        And, ``active=True`` b/c Hotel is in good standing w/ Funds.
        '''
        if self.customer and self.active:
            return True
        else:
            return False

    def get_absolute_url(self):
        return reverse('main:hotel_update', kwargs={'pk':self.pk})

    def set_admin_id(self, user):
        # User
        user.profile.update_hotel(self)
        # Admin Group
        user.groups.add(Group.objects.get(name="hotel_admin"))
        user.save()
        # Hotel
        self.admin_id = user.id
        self.save()
        return self

    def update_customer(self, customer):
        self.customer = customer
        self.save()
        return self

    def update_twilio(self, sid, auth_token):
        self.twilio_sid = sid
        self.twilio_auth_token = auth_token
        self.save()
        return self

    def update_twilio_phone(self, ph_sid, phone_number):
        self.twilio_ph_sid = ph_sid
        self.twilio_phone_number = phone_number
        self.save()
        return self


def profile_image(instance, filename):
    return '/'.join(['profile', filename])


class UserProfile(AbstractBase):
    """
    Admin User Reqs
    ---------------
    #1 Below will call all methods, to confirm that the Hotel 
    Admin is setup correctly.

    1. Set as Admin on the Hotel Obj: ``Hotel.set_admin_id(user)``
    2. The Admin User must have a hotel attr: ``UserProfile.update_hotel(hotel)`` 
    3. Group set: ``user.groups.add(Group.objects.get(name="hotel_admin"))``

    """
    user = models.OneToOneField(User, primary_key=True, related_name='profile')
    hotel = models.ForeignKey(Hotel, blank=True, null=True)
    msg_sign = models.CharField(_("Message Signature"), max_length=25, blank=True)
    thumbnail = models.ImageField(upload_to=profile_image, null=True, blank=True)

    class Meta:
        permissions = (
            ("hotel_admin", "hotel_admin"),
            ("hotel_manager", "hotel_manager"),
        )

    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        """
        2 possible outcomes:
            A. Take 1st letter of FName, Lname. i.e. Bob Cohen == -BC
            B. Use username. i.e. bobby == -bobby
        """
        # TESTING ONLY:
        if not self.thumbnail:
            self.thumbnail = 'profile/54 Illustrated Flat Icons 1_3P9A3ey.gif'
            
        # Auto-Join to group of the Hotel for ``ws4redis`` Group Messaging.
        if self.hotel:
            g, _ = Group.objects.get_or_create(name=self.hotel.group_name)
            self.user.groups.add(g)

        try:
            self.msg_sign = "-{}{}".format(self.user.first_name[0].upper(),
                self.user.last_name[0].upper())
        except IndexError:
            self.msg_sign = "-{}".format(self.user.username)

        return super(UserProfile, self).save(*args, **kwargs)

    @property
    def is_admin(self):
        return 'hotel_admin' in [g.name for g in self.user.groups.all()]

    @property
    def is_manager(self):
        return 'hotel_manager' in [g.name for g in self.user.groups.all()]

    def get_absolute_url(self):
        return reverse('main:user_detail', kwargs={'pk': self.pk})

    def get_absolute_url_managed(self):
        return reverse('main:manage_user_detail', kwargs={'pk': self.pk})

    def update_hotel(self, hotel):
        self.hotel = hotel
        return self.save()

    def hide(self):
        '''
        A Mgr+ can delete any User for their Hotel except the Admin.
        '''
        if self.is_admin:
            raise ValidationError(dj_messages['alter_admin_fail'])
        return super(UserProfile, self).hide()


##############
# SUBACCOUNT #
##############

class SubaccountManager(models.Manager):

    def twilio_create(self, hotel):
        '''User Master sid/auth_token to create a Twilio Subaccount.'''
        client = TwilioRestClient(settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN)
        return client.accounts.create(friendly_name=hotel.name)

    def get_or_create(self, hotel, *args, **kwargs):
        try:
            subaccount = self.get(sid=hotel.twilio_sid)
            return subaccount, False
        except ObjectDoesNotExist:
            subaccount = self.twilio_create(hotel)
            db_subaccount = self.create(
                hotel=hotel,
                sid=subaccount.sid,
                auth_token=subaccount.auth_token)

            # update denormalized Twilio fields
            hotel.update_twilio(sid=subaccount.sid,
                auth_token=subaccount.auth_token)

            return db_subaccount, True
        

class Subaccount(AbstractBase):
    """
    Twilio Subaccount
    -----------------
    To handle API Calls and main entry point for Twilio per Hotel.

    TODO: When customer successfully pays for Account, create a Subaccount
        with a new PhoneNumber.
        - Create "Dave Hotel" Subaccount w/ already created `sid`
    """
    hotel = models.OneToOneField(Hotel, related_name='subaccount')
    sid = models.CharField(_("Twilio Subaccount Sid"), primary_key=True, max_length=100)
    auth_token = models.CharField(_("Auth Token"), max_length=100)
    active = models.BooleanField(_("Active"), blank=True, default=True)

    objects = SubaccountManager()
    
    def __init__(self, *args, **kwargs):
        super(Subaccount, self).__init__(*args, **kwargs)

        # Twilio Client
        self.client = TwilioRestClient(self.sid, self.auth_token)

    def __str__(self):
        return self.sid

    @property
    def twilio_object(self):
        return self.client.accounts.get(self.sid)

    def update_status(self, status):
        '''Update the native Twilio Status, then the DB Status. Used for Hotel 
        Subaccounts not in good standing, or closed.'''

        self.validate_status(status)
        self.client.accounts.update(self.sid, status=status)

        if status == 'active':
            self.active = True
        else:
            self.active = False
            
        return self.save()    

    def validate_status(self, status):
        if status not in (['active', 'suspended', 'closed']):
            raise excp.InvalidSubaccountStatus("{} is an invalid status.".format(status))


'''
DRF Token Auth
--------------
'''
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


'''
Denormalize Hotel
-----------------
Twilio Subaccount attrs denormalized to Hotel.
'''
@receiver(post_save, sender=Subaccount)
def denormalize_twilio_subaccount(sender, instance=None, created=False, **kwargs):
    if created:
        hotel = instance.hotel
        hotel.twilio_sid = instance.sid
        hotel.twilio_auth_token = instance.auth_token
        hotel.save()


'''
UserProfile
-----------
UserProfile.user is a OneToOneField of User, and should not exist unless there
is a User. So Auto create/delete based on User.
'''
@receiver(post_save, sender=User)
def create_userprofile(sender, instance=None, created=False, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(pre_delete, sender=User)
def delete_userprofile(sender, instance=None, **kwargs):
    if instance:
        userprofile = UserProfile.objects.get(user=instance)
        userprofile.delete()