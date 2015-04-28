import pytest

from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist

from model_mommy import mommy

from sms.models import Text, DemoCounter
from utils.exceptions import DailyLimit


class TextTests(TestCase):

    def test_sent(self):
        sent = mommy.make(Text, sent=True)

        texts = Text.objects.all()
        assert len(texts) == 1
        assert isinstance(sent, Text)

        sent_texts = Text.objects.sent()
        assert len(sent_texts) == 1
        assert sent == sent_texts[0]

    def test_not_sent(self):
        not_sent = mommy.make(Text, sent=False)

        texts = Text.objects.all()
        assert len(texts) == 1
        assert isinstance(not_sent, Text)
        
        not_sent_texts = Text.objects.not_sent()
        assert len(not_sent_texts) == 1
        assert not_sent == not_sent_texts[0]


class DemoCounterTests(TestCase):

    def test_delete_all(self):
        dc = mommy.make(DemoCounter)
        delete_all = DemoCounter.objects.delete_all()
        dc_all = DemoCounter.objects.all()
        assert len(dc_all) == 0

    def test_today_no_record(self):
        with pytest.raises(ObjectDoesNotExist):
            today = DemoCounter.objects.today()

    def test_today(self):
        delete_all = DemoCounter.objects.delete_all()
        dc = mommy.make(DemoCounter)
        today = DemoCounter.objects.today()
        assert isinstance(today, DemoCounter)
        assert today.count == 1

    def test_create(self):
        delete_all = DemoCounter.objects.delete_all()
        dc = DemoCounter.objects.create()
        assert isinstance(dc, DemoCounter)
        assert dc.count == 1

    def test_create_count(self):
        delete_all = DemoCounter.objects.delete_all()
        dc = DemoCounter.objects.create_count()
        assert isinstance(dc, DemoCounter)
        assert dc.count == 1

    def test_create_count_increment(self):
        delete_all = DemoCounter.objects.delete_all()
        dc = DemoCounter.objects.create_count()
        dc_two = DemoCounter.objects.create_count()
        assert dc.count + 1 == dc_two.count 

    def test_create_count_raise(self):
        delete_all = DemoCounter.objects.delete_all()
        dc = mommy.make(DemoCounter, count=settings.SMS_LIMIT)

        with pytest.raises(DailyLimit):
            next = DemoCounter.objects.create_count()



