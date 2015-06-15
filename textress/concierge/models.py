import re
import datetime

from django import forms
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.validators import BaseValidator
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _, ungettext_lazy
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_delete
from django.core.exceptions import ObjectDoesNotExist

from main.models import (AbstractBase, AbstractBaseQuerySet, AbstractBaseManager,
    Hotel, UserProfile)
from sms.helpers import send_message

from twilio import TwilioRestException
from twilio.rest import TwilioRestClient
from utils import validate_phone
from utils.exceptions import (CheckOutDateException, ValidSenderException,
    PhoneNumberInUse, ReplyNotFound)


#########
# GUEST #
#########

class GuestQuerySet(AbstractBaseQuerySet):
    
    def get_by_hotel_phone(self, hotel, phone_number):
        try:
            return self.get(hotel=hotel, phone_number=phone_number)
        except ObjectDoesNotExist:
            raise


class GuestManager(AbstractBaseManager, models.Manager):

    def get_queryset(self):
        return GuestQuerySet(self.model, self._db)

    def get_by_hotel_phone(self, hotel, phone_number):
        return self.get_queryset().get_by_hotel_phone(hotel, phone_number)

    def get_or_create_unknown_guest(self, hotel, phone_number, name="Unknown Guest"):
        '''
        Return: Unknown Guest Object, or create one if it doesn't exist.
        '''
        try:
            return self.get(hotel=hotel, phone_number=phone_number)
        except ObjectDoesNotExist:
            return self.create(
                hotel=hotel,
                name="Unknown Guest",
                room_number='0',
                phone_number=phone_number,
                check_in=timezone.today(),
                check_out=timezone.today()
                )
    
    def get_by_phone(self, hotel, phone_number):
        '''Resolve Hotel Guest in this order:
            1. current guest
            2. archived guest
            3. unknown hotel guest
        '''
        try:
            return (self.get_queryset()
                        .current()
                        .get_by_hotel_phone(hotel, phone_number))
        except ObjectDoesNotExist:
            try:
                return (self.get_queryset()
                            .archived()
                            .get_by_hotel_phone(hotel, phone_number))
            except ObjectDoesNotExist:
                return self.get_or_create_unknown_guest(hotel, phone_number)


class Guest(AbstractBase):
    """
    TODO: Change `phone_number` to `unique=True` for production.
    """
    # Keys
    hotel = models.ForeignKey(Hotel)
    # Fields
    name = models.CharField(_("Name"),
        help_text="Full name of the Guest as you would like to call them.",
        max_length=110)
    room_number = models.CharField(_("Room Number"), max_length=10)
    phone_number = models.CharField(_("Phone Number"), db_index=True, max_length=12,
        help_text="10 Digit Phone Number. Example: 7025101234")
    check_in = models.DateField(_("Check-in Date"), blank=True,
        help_text="If left blank, Check-in Date will be today.")
    check_out = models.DateField(_("Check-out Date"), blank=True)
    confirmed = models.BooleanField(_("Confirmed"), blank=True, default=False,
        help_text="Reply 'Y' to Confirm PH # for example.")
    stop = models.BooleanField(_("Stop"), blank=True, default=False,
        help_text="Reply 'S' to Stop receiving all messages.")

    objects = GuestManager()

    def __str__(self):
        return self.name

    @property
    def is_unknown(self):
        return self.name == "Unknown Guest"

    def validate_phone_number_taken(self, phone_number):
        '''Ph # isn't being used by any other current Guests.

        TODO: Should this raise a Form Error instead? Like `validate_phone`?
        '''
        if Guest.objects.current().filter(phone_number=phone_number):
            raise PhoneNumberInUse("{} is currently in use.".format(phone_number))

    def validate_check_in_out(self, check_in, check_out):
        if not check_in:
            check_in = timezone.now().date()

        if not check_out:
            check_out = check_in + datetime.timedelta(days=1)
            
        if check_in > check_out:
            # TODO: check to see if passed to the User that there is
            # and error in their input.
            raise CheckOutDateException(check_in, check_out)

        return (check_in, check_out)

    def save(self, *args, **kwargs):
        '''
        TODO: Add logic to handle a raw 10-digit input ph # by the User.
        '''
        if not self.id:
            self.validate_phone_number_taken(self.phone_number)

        validate_phone(self.phone_number)

        self.check_in, self.check_out = self.validate_check_in_out(
            self.check_in, self.check_out)

        return super(Guest, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('concierge:guest_detail', kwargs={'pk':self.pk})

    def _confirmed(self):
        self.confirmed = True
        return self.save()

    def _stop(self):
        self.stop = True
        return self.save()


###########
# MESSAGE #
###########

class MessageQuerySet(models.query.QuerySet):
    
    def current(self):
        return self.filter(hidden=False)

    def monthly_all(self, date):
        return self.filter(insert_date__month=date.month,
                           insert_date__year=date.year)

    def daily_all(self, date):
        return self.filter(insert_date=date)


class MessageManager(models.Manager):

    def get_queryset(self):
        return MessageQuerySet(self.model, self._db)

    def current(self):
        return self.get_queryset().current()

    def receive_message(self, guest, data):
        """
        TODO: Review this method, test logic.

        NOTES:
        Hotels will have an "Unknown" Guest Messages container, if they
        receive a Message from an unregistered ph #.

        `tm` = Twilio Message Object
        """

        try:
            return self.get(sid=data['SmsSid'])
        except ObjectDoesNotExist:
            try:
                db_message = self.create(
                    guest=guest,
                    sid=data['SmsSid'],
                    received=True,
                    status=data['SmsStatus'],
                    to_ph=data['To'],
                    from_ph=data['From'],
                    body=data['Body']
                    )
            except (ObjectDoesNotExist, Exception) as e:
                # TODO: only reaches this point if the received Twilio Message
                #   failed to save to the DB.
                # this should be logged
                print("{}, {}".format(e.__class__, e))
            else:
                return db_message

    def monthly_all(self, date):
        return self.get_queryset().monthly_all(date)

    def daily_all(self, date):
        return self.get_queryset().daily_all(date)


class Message(AbstractBase):
    """
    All Messages belong to a Guest.
    guest_id/user_id - 1 and only 1 populated for the Sender.

    Required Fields: guest, body
    """
    # Keys
    guest = models.ForeignKey(Guest)
    user = models.ForeignKey(User, blank=True, null=True,
        help_text="NULL unless sent from a Hotel User.")
    hotel = models.ForeignKey(Hotel, related_name='messages', blank=True, null=True)
    # Twilio Fields
    sid = models.CharField(_("Twilio Sid"), unique=True, max_length=55, blank=True, null=True,
        help_text="If the message failed to send, there won't be a Twilio Sid.")
    received = models.NullBooleanField(_("Received"), blank=True, default=False)
    status = models.CharField(_("Status"), max_length=25, blank=True, null=True)
    to_ph = models.CharField(_("To"), max_length=12, blank=True)
    from_ph = models.CharField(_("From"), max_length=12, blank=True,
        default=settings.PHONE_NUMBER)
    body = models.TextField(_("Message"), max_length=320)
    reason = models.CharField(_("Error Code Reason"), max_length=100,
        blank=True, null=True, help_text="Reason for failure of SMS send, else Null.")
    cost = models.FloatField(blank=True, null=True)
    # Auto fields
    insert_date = models.DateField(_("Insert Date"), blank=True, null=True)
    read = models.BooleanField(_("Read"), blank=True, default=False,
        help_text="All messages are unread until rendered in a User View.")

    objects = MessageManager()

    def __str__(self):
        return "Date: {} Guest: {} Msg: {}".format(self.created, self.guest,
            self.msg_short())

    def save(self, *args, **kwargs):
        '''
        Validate Sender. If Guest, send_message()
        '''
        if not self.sid:
            try:
                msg = send_message(hotel=self.guest.hotel, to=self.to_ph, body=self.body)
                msg = msg.__dict__
                self.sid = msg['sid']
                self.cost = msg['price']
                self.reason = msg['error_code']
                self.received = True
                # add User to note the message was sent by a User, not a Guest
                # self.user = 
            except TwilioRestException as e:
                self.reason = e.__dict__['msg']

        self.hotel = self.guest.hotel or self.user.profile.hotel

        # For testing only
        if not self.insert_date:
            self.insert_date = timezone.now().date()

        return super(Message, self).save(*args, **kwargs)  

    def msg_short(self):
        return "{}...".format(' '.join(self.body.split()[:5]))

    def get_absolute_url(self):
        return reverse('concierge:message_detail', kwargs={'pk':self.pk})


#########
# REPLY #
#########

class ReplyManager(models.Manager):

    def get_hotel_reply(self, letter, *args, **kwargs):
        '''Hotel Specific Reply.'''
        hotel = kwargs.get('hotel', Hotel.objects.textress())

        try:
            return self.filter(hotel=hotel).get(letter=letter)
        except ObjectDoesNotExist:
            raise

    def exec_func_call(self, guest, hotel, reply):
        '''Data changes'''
        if reply.func_call and not hotel.is_textress:
            try:
                getattr(guest, reply.func_call)()
            except AttributeError:
                # TODO: add logging - b/c I added a guest Func that doesn't
                #   have a `data change Reply` configured to it.
                raise

    def get_reply(self, guest, hotel, body):
        '''
        Reply resolution:
            - try get() Hotel Reply
            - try get() Textress default Reply
            - no reply
        '''
        try:
            return self.get_hotel_reply(hotel=hotel, letter=body)
        except ObjectDoesNotExist:
            try:
                return self.get_hotel_reply(letter=body)
            except ObjectDoesNotExist:
                raise ReplyNotFound

    def process_reply(self, guest, hotel, body):
        try:
            reply = self.get_reply(guest, hotel, body)
        except ReplyNotFound:
            return
        else:
            self.exec_func_call(guest, hotel, reply)
            return reply


class Reply(AbstractBase):
    '''
    Used for Auto-Replies to Hotel Guests, and data changes at the 
    Guest's request.

    `reply` is for triggered replies to the `Guest` based on an incoming
    SMS Hotel or Default `letter`

    `func_call` used for data changes only. doesn't return a auto-reply msg.
    '''
    hotel = models.ForeignKey(Hotel)
    letter = models.CharField(_("Letter(s)"), max_length=25,
        help_text="Letter(s) will be upper cased automatically. Single letters \
        encouraged for shorter SMS, but not enforced.")
    message = models.CharField(_("Auto Reply Message"), max_length=320, blank=True)
    func_call = models.CharField(_("Function Call"), max_length=100, blank=True,
        help_text="Configure the string name of a function call here for User \
        requested data changes")

    objects = ReplyManager()

    class Meta:
        verbose_name_plural = "Replies"

    def reserved_letter(self, letter):
        '''Reserved letters that are not allowed to be used by the Hotel for
        custom configured replies.'''
        return letter in settings.RESERVED_REPLY_LETTERS

    def save(self, *args, **kwargs):
        self.letter = self.letter.upper()
        if not self.hotel.is_textress and self.reserved_letter(self.letter):
            raise forms.ValidationError("{} is a reserved letter, and can't be \
                configured. Please use a different letter(s).".format(self.letter))
        return super(Reply, self).save(*args, **kwargs)