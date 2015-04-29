from django.test import TestCase
from django.core.urlresolvers import reverse


class ErrorPageTests(TestCase):
    
    def test_404(self):
        response = self.client.get(reverse('404'))
        assert response.status_code == 404

    def test_500(self):
        response = self.client.get(reverse('500'))
        assert response.status_code == 500


class OtherPageTests(TestCase):

    def test_terms(self):
        response = self.client.get(reverse('terms'))
        assert response.status_code == 200
        assert response.context['company']
        assert response.context['LLC']