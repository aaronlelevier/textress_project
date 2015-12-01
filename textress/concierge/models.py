import sys
import datetime
import random
import string

from django.db import models
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from celery import shared_task
from twilio import TwilioRestException

from main.models import Hotel, UserProfile, profile_image, Icon
from sms.helpers import send_message
from utils import validate_phone
from utils.models import BaseModel, BaseQuerySet, BaseManager, TimeStampBaseModel
from utils.exceptions import (CheckOutDateException, ValidSenderException,
    PhoneNumberInUse, ReplyNotFound)

import logging

logger = logging.getLogger(__name__)


#########
# GUEST #
#########

class GuestQuerySet(BaseQuerySet):
    
    def get_by_hotel_phone(self, hotel, phone_number):
        '''
        :pre: 
            - `hotel` is an active hotel in the system
            - `phone_number` is a "Guest's phone_number"
        '''
        try:
            return self.get(hotel=hotel, phone_number=phone_number)
        except ObjectDoesNotExist:
            raise

    def archive(self):
        """
        Archive all Guests that are past their Check-out date.

        This Job will scheduled to run daily, as to keep the Guest Lists clean, 
        and free of checked out guests.
        """
        self.need_to_archive().update(hidden=True)

    def need_to_archive(self):
        today = timezone.now().date()
        return self.filter(check_out__lt=today, hidden=False)


class GuestManager(BaseManager):

    def get_queryset(self):
        return GuestQuerySet(self.model, self._db)

    def get_by_hotel_phone(self, hotel, phone_number):
        return self.get_queryset().get_by_hotel_phone(hotel, phone_number)

    def get_or_create_unknown_guest(self, hotel, phone_number):
        '''
        Return: Unknown Guest Object, or create one if it doesn't exist. 
        Distinct by `phone_number`.
        '''
        try:
            return self.get(hotel=hotel, phone_number=phone_number)
        except Guest.DoesNotExist:
            return self.create(
                hotel=hotel,
                name="Unknown Guest",
                room_number='0',
                phone_number=phone_number,
                check_in=timezone.now(),
                check_out=timezone.now()
                )
    
    def get_by_phone(self, hotel, phone_number):
        '''
        Logic: `phone_numbers` should only be registered to one active 
        Guest at a time, if not active, they may be in an archived record.

        Resolve Hotel Guest in this order:
            1. current guest
            2. archived guest
            3. unknown hotel guest
        '''
        try:
            return (self.get_queryset()
                        .current()
                        .get_by_hotel_phone(hotel, phone_number))
        except Guest.DoesNotExist:
            try:
                return (self.get_queryset()
                            .archived()
                            .get_by_hotel_phone(hotel, phone_number))
            except Guest.DoesNotExist:
                return self.get_or_create_unknown_guest(hotel, phone_number)

    def archive(self):
        self.get_queryset().archive()

    def need_to_archive(self):
        return self.get_queryset().need_to_archive()


class Guest(BaseModel):
    # Keys
    hotel = models.ForeignKey(Hotel)
    # Fields
    name = models.CharField(_("Name"),
        help_text="Full name of the Guest as you would like to call them.",
        max_length=110)
    room_number = models.CharField(_("Room Number"), max_length=10)
    phone_number = models.CharField(_("Phone Number"), max_length=12,
        help_text="Allowed phone number format: (702) 510-5555")
    check_in = models.DateField(_("Check-in Date"), blank=True,
        help_text="If left blank, Check-in Date will be today.")
    check_out = models.DateField(_("Check-out Date"), blank=True)
    confirmed = models.BooleanField(_("Confirmed"), blank=True, default=False,
        help_text="Reply 'Y' to Confirm PH # for example.")
    stop = models.BooleanField(_("Stop"), blank=True, default=False,
        help_text="Reply 'S' to Stop receiving all messages.")
    icon = models.ForeignKey(Icon, blank=True, null=True)

    objects = GuestManager()

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # NOTE: TESTING ONLY:
        if 'test' not in sys.argv:
            if not self.icon:
                self.icon = random.choice(Icon.objects.all())

        self.phone_number = validate_phone(self.phone_number)

        self.validate_phone_number_taken()

        self.check_in, self.check_out = self.validate_check_in_out(
            self.check_in, self.check_out)

        return super(Guest, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # if not self.stop and not settings.DEBUG:
        #     trigger_send_message.delay(self.id, "check_out")
        return super(Guest, self).delete(*args, **kwargs)

    @property
    def is_unknown(self):
        return self.name == "Unknown Guest"

    def validate_phone_number_taken(self):
        """
        Assert PH # isn't being used by any other current Guests.
        """
        if (Guest.objects.current().filter(hotel=self.hotel, phone_number=self.phone_number)
                                   .exclude(id=self.id)
                                   .exists()):
            raise PhoneNumberInUse("{} is currently in use.".format(self.phone_number))

    def validate_check_in_out(self, check_in, check_out):
        """
        This validator is at the `model` level, but there is also a validator 
        for this on the `GuestForm`.
        """
        if not check_in:
            check_in = timezone.now().date()

        if not check_out:
            check_out = check_in + datetime.timedelta(days=1)
            
        if check_in > check_out:
            raise CheckOutDateException(check_in, check_out)

        return (check_in, check_out)

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
        Access the Twilio API, and get_or_create a Message Obj in the DB.

        **Different from ``receive_message_post`` because when quering 
        the Twilio API there are different *Keys* than POSTing to an XML
        endpoint.**

        :guest: Guest Model object
        :data: Twilio Message object as a Dict
        :NOTES:
            Hotels will have an "Unknown" Guest Messages container, if they
            receive a Message from an unregistered ph #.

        Return: Message Obj, Created (Boolean)
        """
        try:
            return self.get(sid=data['sid']), False
        except ObjectDoesNotExist:
            try:
                kwargs = {
                    "guest": guest,
                    "sid": data['sid'],
                    "created": data['date_sent'],
                    "received": True,
                    "status": data['status'],
                    "to_ph": data['to'],
                    "from_ph": data['from_'],
                    "body": data['body']
                }

                # ``receive_message`` shouldn't have a User, unless it's an auto-reply 
                # Message, in which case use the Hotel's Admin User b/c the Message is 
                # coming from the Hotel.
                if data['from_'] == guest.hotel.twilio_phone_number:
                    kwargs.update({
                        "user": guest.hotel.get_admin()
                    })

                db_message = self.create(**kwargs)

            except Exception as e:
                logger.exception(e)
                logger.debug("'MessageManager.receive_message' Failed to save SMS to DB.", exc_info=True)
                return None, None
            else:
                return db_message, True

    def receive_message_post(self, guest, data):
        """
        POSTed kwargs to an XML enpoint are different then the keys when 
        trying to access the Twilio API, so process the key's separately.

        :guest: Guest Model object
        :data: Twilio Message object as a Dict
        :NOTES:
            Hotels will have an "Unknown" Guest Messages container, if they
            receive a Message from an unregistered ph #.
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
                logger.exception(e)
                logger.debug("'MessageManager.receive_message_post' Failed to save SMS to DB.", exc_info=True)
                return None
            else:
                return db_message

    def monthly_all(self, date):
        return self.get_queryset().monthly_all(date)

    def daily_all(self, date):
        return self.get_queryset().daily_all(date)


class Message(BaseModel):
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
    reason = models.CharField(_("Error Code Reason"), max_length=500,
        blank=True, null=True, help_text="Reason for failure of SMS send, else Null.")
    cost = models.FloatField(blank=True, null=True)
    # Auto fields
    insert_date = models.DateField(_("Insert Date"), blank=True, null=True)
    read = models.BooleanField(_("Read"), blank=True, default=False,
        help_text="All messages are unread until rendered in a User View.")

    objects = MessageManager()

    class Meta:
        ordering = ('-created',)

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
                self.read = True
            except TwilioRestException as e:
                self.reason = e.__dict__['msg']

        self.hotel = self.guest.hotel or self.user.profile.hotel

        # For testing only
        if not self.insert_date:
            self.insert_date = timezone.now().date()

        return super(Message, self).save(*args, **kwargs)  

    def msg_short(self):
        return "{}...".format(' '.join(self.body.split()[:5]))


#########
# REPLY #
#########

class ReplyManager(models.Manager):

    def check_for_data_update(self, guest, reply):
        "Currently only support 'stop messages'."
        if reply.letter == "S":
            guest.stop = guest.hidden = True
            guest.save()
        elif reply.letter == "Y":
            guest.stop = guest.hidden = False
            guest.save()

    def get_reply(self, hotel, body):
        '''
        Resolve Reply in this order:

        - Hotel Reply
        - System Reply
        - no reply
        '''
        # cast as uppercase so case-insensitve when receiving from the Guest
        body = body.upper()

        try:
            return self.get(hotel=hotel, letter=body)
        except Reply.DoesNotExist:
            try:
                return self.get(letter=body)
            except Reply.DoesNotExist:
                raise ReplyNotFound

    def process_reply(self, guest, hotel, body):
        """Check for an 'auto-reply'. If one exists, return it, and make 
        an necessary data changes."""
        try:
            reply = self.get_reply(hotel, body)
        except ReplyNotFound:
            return
        else:
            self.check_for_data_update(guest, reply)
            return reply


REPLY_LETTERS = [(x,x) for x in string.ascii_uppercase]


class Reply(TimeStampBaseModel):
    '''
    Used for Auto-Replies to Hotel Guests, and data changes at the 
    Guest's request.

    `reply` is for triggered replies to the `Guest` based on an incoming
    SMS Hotel or System `letter`

    :unique constraint: unique by Hotel, Letter

    :system letters: If Hotel == None, it is a System Reply

    - "S" - stop - block all messages
    - "Y" - reactivate - allow messages again
    '''
    hotel = models.ForeignKey(Hotel, blank=True, null=True)
    letter = models.CharField(_("Letter(s)"), max_length=1,
        choices=REPLY_LETTERS, default=REPLY_LETTERS[0][0],
        help_text="Letter(s) will be upper cased automatically. Single letters "
                  "encouraged for shorter SMS, but not enforced.")
    desc = models.CharField(_("Description"), max_length=254, blank=True)
    message = models.CharField(_("Auto Reply Message"), max_length=320, blank=True)

    objects = ReplyManager()

    class Meta:
        verbose_name_plural = "Replies"

    def __str__(self):
        return "Letter: {}; Hotel: {}".format(self.letter, self.hotel)

    def save(self, *args, **kwargs):
        # All Letters are uppercase by default
        self.letter = self.letter.upper()
        # Validators
        self._validate_unique_constraint()
        self._validate_not_reserved_letter()

        return super(Reply, self).save(*args, **kwargs)

    @staticmethod
    def _reserved_letter(letter):
        '''Reserved letters that are not allowed to be used by the Hotel for
        custom configured replies.'''
        return letter in settings.RESERVED_REPLY_LETTERS

    def _validate_not_reserved_letter(self):
        "System Letter's can't be used by a Hotel"
        if self.hotel and self._reserved_letter(self.letter):
            raise ValidationError(
                "{} is a reserved letter, and can't be configured. "
                "Please use a different letter(s).".format(self.letter)
            )

    def _validate_unique_constraint(self):
        "Must be unique by Hotel, Letter"
        try:
            reply = (Reply.objects.exclude(id=self.id)
                                  .get(hotel=self.hotel, letter=self.letter))
        except Reply.DoesNotExist:
            return
        else:
            raise ValidationError(
                "Reply with letter: '{}' with message: '{}' already "
                "exists.".format(reply.letter, reply.message)
            )


class TriggerType(TimeStampBaseModel):
    """
    Static table to hold "Trigger Types"

    :Types:

    - "check_in"
    - "check_out"
    """
    name = models.CharField(max_length=100, unique=True,
        help_text="name to be referenced in the application code.")
    human_name = models.CharField(max_length=100, blank=True)
    desc = models.CharField(max_length=254, blank=True,
        help_text="Use to store information about what each Trigger type "
                  "will actually do. i.e. 'check_in' will be used to send "
                  "welcome messages.")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.human_name:
            self.human_name = self.name.replace('_', ' ')
        super(TriggerType, self).save(*args, **kwargs)


class TriggerManager(models.Manager):

    def send_message(self, guest_id, trigger_type_name):
        guest = Guest.objects.get(id=guest_id)

        try:
            trigger = self.get(hotel=guest.hotel, type__name=trigger_type_name)
        except Trigger.DoesNotExist:
            return
        else:
            if not guest.stop:
                return Message.objects.create(to_ph=guest.phone_number, guest=guest,
                    user=guest.hotel.get_admin(), body=trigger.reply.message)


class Trigger(TimeStampBaseModel):
    """
    Links Hotel's to a unique ``TriggerType``, to be specified when 
    it will be called in the application code.

    :unique constraint: must be unique by ``TriggerType`` and ``Hotel``

    :Use cases:

    1. At signup, check "check_in" Trigger if need to send?
    2. Day after check-out, check "check_out" Trigger if need to send?

    :Reply FK: b/c Hotel's can configure the Reply letter they want.
    """
    type = models.ForeignKey(TriggerType)
    hotel = models.ForeignKey(Hotel)
    reply = models.ForeignKey(Reply)
    active = models.BooleanField(blank=True, default=False)

    objects = TriggerManager()

    def __str__(self):
        return "Hotel: {}; Trigger Type:{}.".format(self.hotel, self.type)

    def save(self, *args, **kwargs):
        self._validate_type_hotel_unique()
        return super(Trigger, self).save(*args, **kwargs)

    def _validate_type_hotel_unique(self):
        try:
            trigger = (Trigger.objects.exclude(id=self.id)
                                      .get(type=self.type, hotel=self.hotel))
        except Trigger.DoesNotExist:
            pass
        else:
            raise ValidationError(
                "Unique constraint violated, this Trigger exists: {}"
                .format(trigger))
