import os
from os import listdir
from os.path import isfile, join

from django.forms.models import model_to_dict

from concierge.models import Guest, Message, Reply
from main.models import Hotel, Icon
from utils import login_messages


def process_from_messages():
    '''
    TODO: test, and schedule via Celery to make sure all Twilio Messages 
    are in the DB.
    '''
    for guest in Guest.objects.current():
        client = guest.hotel._client
        for message in (sorted(client.messages.list(from_=guest.phone_number),
                        key=lambda message: message.date_sent)):
            Message.objects.receive_message(guest, message.__dict__)


def process_incoming_message(data):
    '''
    `Hotel` to recieve the `Message` must be located, if not, reply 
    with a standard "HNF" `Reply`

    `Guest` resolve before receiving `Message`

    Return:

    - msg: b/c will be converted to JSON and sent to client thro Redis
    - reply: auto-reply to guest TODO: [need to move out of `ReceiveSMSView code]
    - hotel: used for group messaging by Hotel.group_name
    '''
    hotel = Hotel.objects.get_by_phone(data['To'])
    
    guest = Guest.objects.get_by_phone(hotel, data['From'])

    if hotel.is_textress and guest.is_unknown:
        return Message.objects.create(guest=guest, hotel=hotel, to=data['From'],
            body=login_messages['hotel_not_found'])

    # save message to DB
    msg = Message.objects.receive_message_post(guest, data)

    reply = Reply.objects.process_reply(guest, hotel, data['Body'])

    return msg, reply, hotel


def generate_icon_fixtures():
    mypath = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'media/icons')
    print mypath
    mypath = '/Users/aaron/Documents/djcode/textra_project/textress/media/icons/'
    onlyfiles = [f for f in listdir(mypath) 
                 if isfile(join(mypath,f))]
    for i in Icon.objects.all():
        i.delete()
    for f in onlyfiles:
        Icon.objects.get_or_create(icon='icons/{}'.format(f))