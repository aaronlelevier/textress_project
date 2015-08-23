import string
import random

from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.utils import timezone

from model_mommy import mommy

from rest_framework import status
from rest_framework.test import APITestCase

from main.models import Hotel, UserProfile
from concierge.models import Guest, Message

# Test Factory Imports
from concierge import views, serializers
from concierge.tests.factory import make_guests, make_messages
from main.models import Hotel, UserProfile
from main.tests.factory import create_hotel, create_hotel_user, PASSWORD
from utils import create, dj_messages

from main.tests.factory import create_hotel


def number(limit=10):
    ret = ''.join([str(x) for d in range(limit) 
                           for x in random.choice(string.digits)])
    return "{}-{}-{}".format(ret[:3], ret[3:6], ret[6:])


def today():
    d = timezone.now().date()
    return d.strftime("%Y-%m-%d")


class GuestViewTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()

        # set User "aaron_test" from fixtures as an attr on this class
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, group='hotel_admin')

        self.guests = make_guests(self.hotel)
        self.guest = self.guests.first()

        # Login
        self.client.login(username=self.user.username, password=PASSWORD)

    def tearDown(self):
        self.client.logout()

    def test_list(self):
        self.client.logout()
        # Dave is not logged in, so get's a 403 response
        response = self.client.get(reverse('concierge:guest_list'))
        self.assertEqual(response.status_code, 302) #login

    def test_list_ok(self):
        # Dave now tries Logged-In        
        response = self.client.get(reverse('concierge:guest_list'))
        self.assertEqual(response.status_code, 200)
        assert response.context['object_list']

    def test_detail(self):
        # Get Guest's details
        response = self.client.get(reverse('concierge:guest_detail', kwargs={'pk': self.guest.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['object'], self.guest)
        self.assertIn(reverse('concierge:guest_list'), response.content)

    def test_detail_unread_messages(self):
        # 10 unread messages at start, but after going to the Guest's 
        # Detail view, they are bulk updated as "read=True"
        messages = make_messages(
            hotel=self.hotel,
            user=self.user,
            guest=self.guest
        )
        Message.objects.filter(guest=self.guest).update(read=False)
        self.assertEqual(Message.objects.filter(guest=self.guest).count(), 10)
        self.assertEqual(Message.objects.filter(guest=self.guest, read=True).count(), 0)
        # Go to Detail View n trigger Update
        response = self.client.get(reverse('concierge:guest_detail', kwargs={'pk': self.guest.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Message.objects.filter(guest=self.guest, read=True).count(), 10)

    def test_delete_guests(self):
        # No guests
        [g.delete() for g in Guest.objects.all()]
        self.assertEqual(Guest.objects.count(), 0)

    def test_create(self):
        [g.delete() for g in Guest.objects.all()]

        # Login n Create a Guest
        response = self.client.post(reverse('concierge:guest_create'),
            {'hotel':self.user.profile.hotel,
            'name': 'Test Guest',
            'room_number': number(5),
            'phone_number': number(),
            'check_in': today(),
            'check_out': today()},
            follow=True)

        # Now 1 guest
        guest = Guest.objects.first()
        self.assertIsInstance(guest, Guest)
        self.assertRedirects(response, reverse('concierge:guest_detail', kwargs={'pk':guest.pk}))

    def test_update_get(self):
        response = self.client.get(reverse('concierge:guest_update', kwargs={'pk':self.guest.pk}))
        self.assertEqual(response.status_code, 200)

    def test_update_post(self):
        guest_info_dict = {
            'hotel': self.guest.hotel,
            'name': self.guest.name,
            'room_number': number(5),
            'phone_number': number(),
            'check_in': today(),
            'check_out': today()
            }

        # update in View
        guest_info_dict['name'] = 'Updated Name'
        # POST  
        response = self.client.post(reverse('concierge:guest_update', kwargs={'pk':self.guest.pk}),
            guest_info_dict, follow=True)
        self.assertRedirects(response, reverse('concierge:guest_detail', kwargs={'pk': self.guest.pk}))
        new_guest = Guest.objects.get(name=guest_info_dict['name'])
        self.assertNotEqual(self.guest.name, new_guest.name)

    def test_delete(self):
        guest = Guest.objects.first()
        self.assertTrue(isinstance(guest, Guest))
        self.assertFalse(guest.hidden)

        # Hide
        response = self.client.post(reverse('concierge:guest_delete', kwargs={'pk': guest.pk}),
            {}, follow=True)
        self.assertRedirects(response, reverse('concierge:guest_list'))
        # hide guest worked
        updated_guest = Guest.objects.get(pk=guest.pk)
        self.assertTrue(updated_guest.hidden)


########
# REST #
########

class MessageAPITests(APITestCase):

    def setUp(self):
        # Groups
        create._get_groups_and_perms()
        self.password = PASSWORD
        # User
        self.hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, group='hotel_admin')
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
        response = self.client.get(reverse('concierge:api_messages'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_message_required_objects(self):
        # Make sure all objects needed to send a message have been created
        # if not, maybe need to change .create() in APIView
        hotel = self.admin.profile.hotel
        assert isinstance(hotel, Hotel)

        guest = Guest.objects.get(pk=self.guest.id,
                hotel=hotel)
        assert isinstance(guest, Guest)

    # /api/messages/<pk>/

    def test_get_message_pk(self):
        message = Message.objects.filter(guest=self.guest)[0]
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('concierge:api_messages', kwargs={'pk': message.pk}))
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
        response = self.client.get(reverse('concierge:api_guest_messages'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # TODO: Test other guests can't be rendered


class GuestAPITests(APITestCase):

    def setUp(self):
        # Groups
        create._get_groups_and_perms()
        self.password = PASSWORD
        # User
        self.hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, group='hotel_admin')
        self.hotel.admin_id = self.admin.id
        self.hotel.save()

        # Guest
        self.guest = make_guests(hotel=self.hotel, number=1)[0] #b/c returns a list

        self.data = {'name': 'mike', 'room_number': '123',
                     'phone_number': settings.DEFAULT_TO_PH_2}

    # /api/guests/

    def test_get_list(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('concierge:api_guests'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.post(reverse('concierge:api_guests'), self.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # /api/guests/<pk>/

    def test_get_guest_pk(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('concierge:api_guests', kwargs={'pk': self.guest.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update(self):
        self.client.login(username=self.admin.username, password=self.password)
        self.data = serializers.GuestBasicSerializer(self.guest).data
        self.data.update({'name': 'changed'})

        response = self.client.get(reverse('concierge:api_guests', kwargs={'pk': self.guest.pk}), self.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)