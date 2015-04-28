import pytest
import stripe

from django import forms
from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
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

        for name in ['hotel_admin', 'hotel_manager']:
            assert isinstance(Group.objects.get(name=name), Group)
            assert isinstance(Permission.objects.get(name=name), Permission)

    def test_get_users(self):
        # create._get_groups_and_perms()

        users = create._get_users()
        for user in users:
            assert isinstance(user, User)

        for name in ['hotel_admin', 'hotel_manager']:
            # g = Group.objects.get(name=name)
            admin_users = User.objects.filter(groups__name=name)
            assert len(admin_users) == 5

    def test_get_hotels(self):
        hotels = create._get_hotels()
        assert len(hotels) == 5

    def test_phone_numbers(self):
        phones = create._phone_numbers()
        assert len(phones) == 5

    def test_get_guests(self):
        guests = create._get_guests()
        assert len(guests) == 5

    def test_create_main(self):
        create.create_main()

        groups = ['hotel_admin', 'hotel_manager']
        for name in groups:
            assert len(User.objects.filter(groups__name=name)) == 5

        # 3 Users p/Hotel. 1 of ea. Permission Group
        hotels = create._get_hotels()
        for hotel in hotels:
            assert len(UserProfile.objects.filter(hotel=hotel)) == 3

        # creates 25 Messages, 5 Msg p/Guest
        assert len(Message.objects.all()) == 25

    def test_remove_all(self):
        create.remove_all()
        models = [User, Group, Permission, UserProfile, Hotel, Guest, Message]
        for m in models:
            assert not m.objects.all()

    def test_clean_userprofiles(self):
        # Signal on User Model auto-creates UserProfile
        user = mommy.make(User)
        assert len(User.objects.all()) == 1
        assert len(UserProfile.objects.all()) == 1

        # Remove UserProfile
        user_profile = UserProfile.objects.get(user=user)
        user_profile.delete()
        assert len(UserProfile.objects.all()) == 0

        # should add back missing UserProfile(s)
        create.clean_userprofiles()
        assert len(UserProfile.objects.all()) == 1

    def test_superuser_profile(self):
        create.superuser_profile()
        assert len(User.objects.filter(is_superuser=True)) == 1

    def test_create_all(self):
        """
        15 Users
        5 Hotels
        2 User Groups
        1 of ea. type p/Hotel
        5 Guests, 1 in ea. Hotel
        """
        create.create_all()
        data = [(User, 15), (Hotel, 5), (Group, 2), (Guest, 5), (Hotel, 5), (Message, 25)]
        for model, count in data:
            try:
                m_count = model.objects.all()
                assert len(m_count) == count
            except AssertionError as e:
                print("{} Count:{} != {}".format(model, m_count, count))