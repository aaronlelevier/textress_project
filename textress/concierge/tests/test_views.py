import pytest
import string
import random
import requests

from django.db import models, transaction, IntegrityError
from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.http import Http404
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from model_mommy import mommy

from rest_framework import status
from rest_framework.test import (APIRequestFactory, force_authenticate, APIClient,
    APITestCase)

from main.models import Hotel, UserProfile
from utils.create import create_all
from concierge.models import Guest, Message

# Test Factory Imports
from concierge import views, serializers
from concierge.tests.factory import make_guests, make_messages
from main.models import Hotel, UserProfile
from main.tests.factory import create_hotel
from utils import create

from main.tests.factory import create_hotel


def number(limit=10):
    return ''.join([str(x) for d in range(limit) 
                           for x in random.choice(string.digits)])


def today():
    return timezone.now().date()


class GlobalTests(TestCase):

    def test_ph_num(self):
        ph = number()
        assert len(ph) == 10
        assert type(int(ph)) == int


class GuestViewTests(TestCase):

    def setUp(self):

        self.password = "1234"

        # User0
        self.user = mommy.make(User, username="Test")
        self.user.set_password(self.password)
        self.user.save()

        self.hotel = create_hotel(name="Test")
        self.user.profile.update_hotel(hotel=self.hotel)

    def test_list(self):
        self.client.login(username=self.user.username, password=self.password)

        guest = mommy.make(Guest, hotel=self.hotel)
        response = self.client.get(reverse('concierge:guest_list'))
        assert response.status_code == 200
        assert response.context['object_list']

    def test_detail(self):
        self.client.login(username=self.user.username, password=self.password)

        # Now 1 guest
        guest = mommy.make(Guest, hotel=self.hotel)

        # Get Guest's details\
        response = self.client.get(reverse('concierge:guest_detail', kwargs={'pk': guest.pk}))
        assert response.status_code == 200
        assert response.context['object'] == guest

    def test_create(self):
        # No guests
        (g.delete() for g in Guest.objects.all())

        # Login n Create One
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(reverse('concierge:guest_create'),
            {'hotel':self.user.profile.hotel, 'name': 'Test Guest',
            'room_number': number(5), 'phone_number': number(),
            'check_in': today(), 'check_out': today()},
            follow=True)

        # Now 1 guest
        guest = Guest.objects.get(name='Test Guest')
        assert isinstance(guest, Guest)
        self.assertRedirects(response, reverse('concierge:guest_detail', kwargs={'pk': guest.pk}))

    def test_update(self):
        self.client.login(username=self.user.username, password=self.password)

        # No guests
        (g.delete() for g in Guest.objects.all())

        guest = mommy.make(Guest, name='Test Guest', hotel=self.hotel)
        assert guest.name == 'Test Guest'

        # update in View
        response = self.client.post(reverse('concierge:guest_update', kwargs={'pk':guest.pk}),
            {'hotel':self.user.profile.hotel, 'name': 'Test Guest New',
            'room_number': number(5), 'phone_number': number(),
            'check_in': today(), 'check_out': today()},
            follow=True)

        # Modified Guest
        guest = Guest.objects.first()
        assert guest.name == 'Test Guest New'
        self.assertRedirects(response, reverse('concierge:guest_detail', kwargs={'pk': guest.pk}))

    def test_delete(self):
        self.client.login(username=self.user.username, password=self.password)
        guest = mommy.make(Guest, hotel=self.hotel)
        assert isinstance(guest, Guest)
        assert guest.hidden == False
        # Hide
        response = self.client.post(reverse('concierge:guest_delete', kwargs={'pk': guest.pk}),
            {}, follow=True)
        updated_guest = Guest.objects.get(pk=guest.pk)
        assert updated_guest.hidden == True
        self.assertRedirects(response, reverse('concierge:guest_list'))


########
# REST #
########

class MessageAPITests(APITestCase):

    def setUp(self):
        self.password = '1234'
        self.today = timezone.now().date()

        # Hotel
        self.hotel = create_hotel()

        # create "Hotel Manager" Group
        create._get_groups_and_perms()

        # Admin
        self.admin = mommy.make(User, username='admin')
        self.admin.groups.add(Group.objects.get(name="hotel_admin"))
        self.admin.set_password(self.password)
        self.admin.save()
        self.admin.profile.update_hotel(hotel=self.hotel)
        # Hotel Admin ID
        self.hotel.admin_id = self.admin.id
        self.hotel.save()

        # Guest
        self.guest = make_guests(hotel=self.hotel, number=1)[0] #b/c returns a list
        
        # Messages
        self.messages = make_messages(
            hotel=self.hotel,
            user=self.admin,
            guest=self.guest
            )

        self.data = {'guest': self.guest.pk, 'user': self.admin.pk, 'hotel': self.hotel,
            'to_ph': '+17754194000', 'body':'curl test', 'from_ph': '+17028324062'}

    # /api/messages/

    def test_get(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('api_messages'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_message_required_objects(self):
        # Make sure all objects needed to send a message have been created
        # if not, maybe need to change .create() in APIView
        hotel = self.admin.profile.hotel
        assert isinstance(hotel, Hotel)

        guest = Guest.objects.get(pk=self.guest.id,
                hotel=hotel)
        assert isinstance(guest, Guest)

    def test_message_create(self):
        '''
        User Localhost b/c testserver / APIClient() still wip.
        '''
        r = requests.post('http://localhost:8000/api/messages/',
                          data={"guest": 37,"user": 44,"hotel": 23,"to_ph": "+17754194000",
                                "body":"curl test","from_ph": "+17028324062"},
                          auth=('dave', '1234'))
        
        print(r.status_code)
        assert r.status_code == 201

    # /api/messages/<pk>/

    def test_get_message_pk(self):
        message = Message.objects.filter(guest=self.guest)[0]
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('api_messages', kwargs={'pk': message.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class GuestMessageAPITests(APITestCase):

    def setUp(self):
        self.password = '1234'
        self.today = timezone.now().date()

        # Hotel
        self.hotel = create_hotel()

        # create "Hotel Manager" Group
        create._get_groups_and_perms()

        # Admin
        self.admin = mommy.make(User, username='admin')
        self.admin.groups.add(Group.objects.get(name="hotel_admin"))
        self.admin.set_password(self.password)
        self.admin.save()
        self.admin.profile.update_hotel(hotel=self.hotel)
        # Hotel Admin ID
        self.hotel.admin_id = self.admin.id
        self.hotel.save()

        # Guest
        self.guest = make_guests(hotel=self.hotel, number=1)[0] #b/c returns a list
        
        # Messages
        self.messages = make_messages(
            hotel=self.hotel,
            user=self.admin,
            guest=self.guest
            )

    def test_get(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('api_guest_messages'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # TODO: Test other guests can't be rendered


class GuestAPITests(APITestCase):

    def setUp(self):
        self.password = '1234'
        self.today = timezone.now().date()

        # Hotel
        self.hotel = create_hotel()

        # create "Hotel Manager" Group
        create._get_groups_and_perms()

        # Admin
        self.admin = mommy.make(User, username='admin')
        self.admin.groups.add(Group.objects.get(name="hotel_admin"))
        self.admin.set_password(self.password)
        self.admin.save()
        self.admin.profile.update_hotel(hotel=self.hotel)
        # Hotel Admin ID
        self.hotel.admin_id = self.admin.id
        self.hotel.save()

        # Guest
        self.guest = make_guests(hotel=self.hotel, number=1)[0] #b/c returns a list

        self.data = {'name': 'mike', 'room_number': '123',
                     'phone_number': settings.DEFAULT_TO_PH}

    # /api/guests/

    def test_get_list(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('api_guests'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.post(reverse('api_guests'), self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # /api/guests/<pk>/

    def test_get_guest_pk(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('api_guests', kwargs={'pk': self.guest.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        self.client.login(username=self.admin.username, password=self.password)
        self.data = serializers.GuestBasicSerializer(self.guest).data
        self.data.update({'name': 'changed'})

        response = self.client.get(reverse('api_guests', kwargs={'pk': self.guest.pk}), self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserAPITests(APITestCase):

    def setUp(self):
        self.password = '1234'
        self.today = timezone.now().date()

        # Hotel
        self.hotel = create_hotel()

        # create "Hotel Manager" Group
        create._get_groups_and_perms()

        # Admin
        self.admin = mommy.make(User, username='admin')
        self.admin.groups.add(Group.objects.get(name="hotel_admin"))
        self.admin.set_password(self.password)
        self.admin.save()
        self.admin.profile.update_hotel(hotel=self.hotel)
        # Hotel Admin ID
        self.hotel.admin_id = self.admin.id
        self.hotel.save()

        self.data = {'username': 'mike', 'first_name': 'Mike', 'last_name': 'Tyson'}

    # /api/users/

    def test_can_get_users(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('api_users'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_create_user(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.post(reverse('api_users'), self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # /api/users/<pk>/

    def test_can_get_users_pk(self):
        user = mommy.make(User)
        user.profile.update_hotel(self.hotel)
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('api_users', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_can_update(self):
        user = mommy.make(User)
        user.profile.update_hotel(self.hotel)
        self.client.login(username=self.admin.username, password=self.password)
        self.data = serializers.UserSerializer(user).data
        self.data.update({'first_name': 'changed'})

        response = self.client.get(reverse('api_users', kwargs={'pk': user.pk}), self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)









