import datetime

from django.test import TestCase
from django.contrib.auth.models import Group, Permission, User
from django.core.management import execute_from_command_line
from django.utils import timezone

from model_mommy import mommy

from main.models import Hotel, UserProfile
from main.tests.factory import create_hotel
from concierge.models import Guest, Message
from utils import create
from utils.tests.runners import celery_set_eager


class CreateTests(TestCase):

    def test_random_lorem(self):
        self.assertTrue(create.random_lorem())

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


class MgmtCmdTests(TestCase):

    def setUp(self):
        celery_set_eager()
        self.yesterday = timezone.now().date() - datetime.timedelta(days=1)
        self.hotel = create_hotel()
        self.guest_to_archive = mommy.make(
            Guest,
            name=create._generate_name(),
            hotel=self.hotel,
            check_in=self.yesterday,
            check_out=self.yesterday,
            phone_number=create._generate_ph()
        )

    def test_archive_guests(self):
        self.assertEqual(Guest.objects.need_to_archive().count(), 1)

        execute_from_command_line(['manage.py'] + ['archive_guests'])
        
        self.assertEqual(Guest.objects.need_to_archive().count(), 0)
