from django.test import TestCase
from django.core.urlresolvers import reverse

from model_mommy import mommy

from contact.models import QA


class Index(TestCase):

    def setUp(self):
        qas = mommy.make(QA, _quantity=3)
        
    def test_get(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'frontend/index.html')
        assert response.context['form']
        assert response.context['topics']


class Error(TestCase):
    
    def test_404(self):
        response = self.client.get(reverse('404'))
        assert response.status_code == 404

    def test_500(self):
        response = self.client.get(reverse('500'))
        assert response.status_code == 500