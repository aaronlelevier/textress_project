from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError

from model_mommy import mommy

from contact.forms import NewsletterForm, ContactForm
from contact.models import Newsletter, Contact
from utils.messages import dj_messages


class ContactTests(TestCase):

    def setUp(self):
        self.data = {
            'name': 'test',
            'email': settings.DEFAULT_EMAIL_SAYHELLO,
            'subject': 'test subject',
            'message': 'test message'
        }

    def test_post(self):
        # success
        response = self.client.post(reverse('index'), self.data, follow=True)
        self.assertRedirects(response, reverse('index'))
        assert isinstance(Contact.objects.first(), Contact)
        
        # success message
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        self.assertEqual(str(m[0]), dj_messages['contact_thanks'])