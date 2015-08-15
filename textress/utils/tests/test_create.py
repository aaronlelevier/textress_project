from django.test import TestCase
from django.contrib.auth.models import Group, Permission, User

from model_mommy import mommy

from utils import create
from concierge.models import Guest, Message
from main.models import Hotel, UserProfile


class CreateTests(TestCase):

    def test_random_lorem(self):
        assert create.random_lorem()

    def test_get_groups_and_perms(self):
        create._get_groups_and_perms()
        self.assertEqual(Group.objects.count(), 2)

    def test_generate_ph(self):
        self.assertTrue(create._generate_ph())

    def test_generate_name(self):
        self.assertTrue(create._generate_name())

    def test_phone_numbers(self):
        phs = create._phone_numbers()
        self.assertTrue(phs)
        self.assertIsInstance(phs, list)