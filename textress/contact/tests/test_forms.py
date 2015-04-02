from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse

from contact.models import Newsletter


class ComingSoonTests(TestCase):

    def test_post(self):
        response = self.client.post(reverse('contact:coming_soon'),
            {'email': settings.DEFAULT_EMAIL_SAYHELLO},
            follow=True)