from django.test import TestCase

from ..helpers import process_from_messages
from ..models import Message


class HelperTests(TestCase):

    fixtures = ['concierge.json', 'main.json']

    def test_receive(self):
        # Send myself a Message b/4 running this test
        msg_start = len(Message.objects.exclude(sid__isnull=True))
        process_from_messages()
        msg_after = len(Message.objects.exclude(sid__isnull=True))
        print(msg_start)
        print(msg_after)
        assert msg_start == msg_after