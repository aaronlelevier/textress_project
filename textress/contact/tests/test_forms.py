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


class ComingSoonTests(TestCase):
    '''
    Redirects to self 
    creates a unique new signup only
    displays a dj-message after success
    '''

    def test_post(self):
        response = self.client.post(reverse('contact:coming_soon'),
            {'email': settings.DEFAULT_EMAIL_SAYHELLO},
            follow=True)
        self.assertRedirects(response, reverse('contact:coming_soon'))
        assert Newsletter.objects.first()

        # dj-messages
        m = list(response.context['messages'])
        assert len(m) == 1
        assert str(m[0]) == dj_messages['coming_soon']

    def test_post_same_email(self):
        # all emails must be unique
        nl = mommy.make(Newsletter, email=settings.DEFAULT_EMAIL_SAYHELLO)
        assert isinstance(nl, Newsletter)

        response = self.client.post(reverse('contact:coming_soon'),
            {'email': settings.DEFAULT_EMAIL_SAYHELLO})
        self.assertFormError(response, 'form', 'email', NewsletterForm.error_messages['already'])
        