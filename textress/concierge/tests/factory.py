import random
import datetime

from django.db import models
from django.conf import settings
from django.utils import timezone

from model_mommy import mommy

from ..models import Message, Guest


def make_guests(hotel, number=10):
    today = timezone.now().date()

    for i in range(number):
        check_out = today + datetime.timedelta(days=random.randrange(1,6))
        mommy.make(Guest, hotel=hotel,
            name="Guest{}".format(str(i)),
            check_in=today,
            check_out=check_out,
            phone_number=settings.DEFAULT_TO_PH)

    return Guest.objects.filter(hotel=hotel)


def make_messages(hotel, user, guest, insert_date=timezone.now().date(), number=10):
    '''
    Randomly choose if the Guest or User is sending the Message.
    Then fill in the details.

    `number` - the number of sent messegas in the b/n the Guest n User.
    '''
    # Monkey-patch Message so as not to send live SMS
    global Message
    Message.save = models.Model.save

    for i in range(number):

        # Randomly chose Message sender.
        sender = random.choice([True, False])

        # Guest Sender
        if sender:
            mommy.make(Message,
                hotel=hotel,
                guest=guest,
                user=None,
                to_ph=settings.DEFAULT_FROM_PH,
                from_ph=settings.DEFAULT_TO_PH,
                insert_date=insert_date,
                read=True
                )
        # User Sender
        else:
            mommy.make(Message,
                hotel=hotel,
                guest=guest,
                user=user,
                to_ph=settings.DEFAULT_TO_PH,
                from_ph=settings.DEFAULT_FROM_PH,
                insert_date=insert_date,
                read=True
                )

    return Message.objects.filter(hotel=hotel)



