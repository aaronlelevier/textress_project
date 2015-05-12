from django.test import TestCase
from django.core.urlresolvers import reverse

from contact.models import Newsletter


class ComingSoonTests(TestCase):

    def test_get(self):
        response = self.client.get(reverse('contact:coming_soon'))
        assert response.status_code == 200
        assert response.context['form']
