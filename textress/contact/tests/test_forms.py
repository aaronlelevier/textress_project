from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse

from contact.models import Newsletter
from utils.messages import dj_messages


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
        assert response.context['message'] == dj_messages['coming_soon']

