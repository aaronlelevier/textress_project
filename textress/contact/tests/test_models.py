from django.test import TestCase

from contact.models import Newsletter

from model_mommy import mommy


class NewsletterTests(TestCase):

    def test_create(self):
        nl = mommy.make(Newsletter)
        assert isinstance(nl, Newsletter)
        assert nl.created
        assert str(nl) == nl.email