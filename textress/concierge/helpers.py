from django.core.exceptions import ObjectDoesNotExist

from .models import Guest, Message, Reply
from account.helpers import login_messages
from main.models import Hotel
from utils import exceptions as excp


def process_from_messages():
    '''
    TODO: test, and schedule via Celery to make sure all Twilio Messages 
    are in the DB.
    '''
    for guest in Guest.objects.current():
        client = guest.hotel._client
        for message in (sorted(client.messages.list(from_=guest.phone_number),
                        key=lambda message: message.date_sent)):
            Message.objects.receive_message(guest, message)


def process_incoming_message(data):
    '''
    `Hotel` to recieve the `Message` must be located, if not, reply 
    with a standard "HNF" `Reply`

    `Guest` resolve before receiving `Message`
    '''
    hotel = Hotel.objects.get_by_phone(data['To'])
    
    guest = Guest.objects.get_by_phone(hotel, data['From'])

    if hotel.is_textress and guest.is_unknown:
        return Message.objects.create(guest=guest, hotel=hotel, to=data['From'],
            body=login_messages['hotel_not_found'])

    # save message to DB
    db_message = Message.objects.receive_message(guest, data)

    return Reply.objects.process_reply(guest, hotel, data['Body'])