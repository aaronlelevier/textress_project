import pytest

from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from model_mommy import mommy

from sms.models import Text


class URLTests(TestCase):

    def test_DemoView_get(self):
        response = self.client.get(reverse('sms:demo'))
        assert response.status_code == 200
