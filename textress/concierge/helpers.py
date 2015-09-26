import os
from os import listdir
from os.path import isfile, join

from django.forms.models import model_to_dict

from rest_framework.renderers import JSONRenderer
from ws4redis.publisher import RedisPublisher
from ws4redis.redis_store import RedisMessage

from concierge.models import Guest, Message, Reply
from main.models import Hotel, Icon
from utils import login_messages


def convert_to_json_and_publish_to_redis(msg):
    redis_publisher = RedisPublisher(facility='foobar', broadcast=True)
    msg = JSONRenderer().render(model_to_dict(msg))
    msg = RedisMessage(msg)
    redis_publisher.publish_message(msg)


def guest_twilio_messages(guest, date):
    client = guest.hotel._client
    for msg in (sorted(client.messages.list(from_=guest.phone_number, date=date),
                       key=lambda message: message.date_sent))]
    

def merge_twilio_messages_to_db(guest, date):
    """Adds Twilio Messages that are not in the DB to the DB.

    Returns: DB Message object ``list``
    """
    messages = []
    for message in guest_twilio_messages(guest, date):
        obj, created = Message.objects.receive_message(guest, message.__dict__)
        if created:
            messages.append(obj)
    return messages


def process_incoming_message(data):
    '''
    `Hotel` to recieve the `Message` must be located, if not, reply
    with a standard "HNF" `Reply`

    `Guest` resolve before receiving `Message`

    Return:

    - msg: b/c will be converted to JSON and sent to client thro Redis
    - reply: auto-reply to guest TODO: [need to move out of `ReceiveSMSView code]
    '''
    hotel = Hotel.objects.get_by_phone(data['To'])

    guest = Guest.objects.get_by_phone(hotel, data['From'])

    if guest.is_unknown:
        return Message.objects.create(guest=guest, hotel=hotel, to=data['From'],
                                      body = login_messages['hotel_not_found'])

    # save message to DB
    msg=Message.objects.receive_message_post(guest, data)

    # If a 'reply' is returned here, it is an auto-reply, and will
    # be sent back to the Guest.
    reply=Reply.objects.process_reply(guest, hotel, data['Body'])

    return msg, reply


def generate_icon_fixtures():
    mypath=os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'media/icons')

    mypath = '/Users/aaron/Documents/djcode/textra_project/textress/media/icons/'
    onlyfiles = [f for f in listdir(mypath)
                 if isfile(join(mypath, f))]
    for i in Icon.objects.all():
        i.delete()
    for f in onlyfiles:
        Icon.objects.get_or_create(icon='icons/{}'.format(f))
