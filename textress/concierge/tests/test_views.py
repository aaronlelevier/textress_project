import string
import random
import json

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
from concierge.models import Reply, REPLY_LETTERS, TriggerType, Trigger
from concierge.tests.factory import make_guests, make_messages
from main.models import Hotel, UserProfile
from main.tests.factory import create_hotel, create_hotel_user, PASSWORD
from utils import create, dj_messages

from main.tests.factory import create_hotel


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
        [g.delete(override=True) for g in Guest.objects.all()]
        self.assertEqual(Guest.objects.count(), 0)

    def test_create(self):
        [g.delete(override=True) for g in Guest.objects.all()]

        # Login n Create a Guest
        response = self.client.post(reverse('concierge:guest_create'),
            {'hotel':self.user.profile.hotel,
            'name': 'Test Guest',
            'room_number': create._generate_int(5),
            'phone_number': create._generate_ph(),
            'check_in': create._generate_date(),
            'check_out': create._generate_date()},
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
            'room_number': create._generate_int(5),
            'phone_number': create._generate_ph(),
            'check_in': create._generate_date(),
            'check_out': create._generate_date()
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

    ### ReplyView

    def test_replies(self):
        response = self.client.get(reverse('concierge:replies'))
        self.assertEqual(response.status_code, 200)


########
# REST #
########

class MessagAPIViewTests(APITestCase):

    def setUp(self):
        # Groups
        create._get_groups_and_perms()
        self.password = PASSWORD
        # User
        self.hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, group='hotel_admin')
        # Guest
        self.guest = make_guests(hotel=self.hotel, number=1)[0] #b/c returns a list
        # Messages
        self.messages = make_messages(
            hotel=self.hotel,
            user=self.admin,
            guest=self.guest
            )

        self.data = serializers.MessageRetrieveSerializer(
            Message.objects.filter(hotel=self.hotel).first()
            ).data

        # Hotel2
        self.hotel2 = create_hotel()
        self.admin2 = create_hotel_user(self.hotel2, username='admin2', group='hotel_admin')
        self.guest2 = make_guests(hotel=self.hotel2, number=1)[0]
        self.messages = make_messages(
            hotel=self.hotel2,
            user=self.admin2,
            guest=self.guest2
            )

        # Login
        self.client.login(username=self.admin.username, password=self.password)

    def tearDown(self):
        self.client.logout()

    def test_create(self):
        self.assertEqual(Message.objects.count(), 20)
        self.assertEqual(Message.objects.filter(hotel=self.hotel).count(), 10)

    ### MessageListCreateAPIView

    def test_list(self):
        response = self.client.get(reverse('concierge:api_messages'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 10)

    def test_list_no_other_hotel_messages(self):
        response = self.client.get(reverse('concierge:api_messages'))
        data = json.loads(response.content)
        for d in data:
            msg = Message.objects.get(id=d['id'])
            self.assertEqual(msg.hotel, self.admin.profile.hotel)

    ### MessageRetrieveAPIView

    def test_detail(self):
        message = Message.objects.filter(hotel=self.hotel).first()
        response = self.client.get(reverse('concierge:api_messages', kwargs={'pk':message.pk}))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['id'], message.pk)

    def test_detail_other_hotel_messages(self):
        message = Message.objects.exclude(hotel=self.hotel).first()
        self.assertIsInstance(message, Message)
        response = self.client.get(reverse('concierge:api_messages', kwargs={'pk':message.pk}))
        self.assertEqual(response.status_code, 403)

    def test_detail_put(self):
        self.assertFalse(self.data['hidden'])
        self.data['hidden'] = True
        response = self.client.put(reverse('concierge:api_messages', kwargs={'pk':self.data['id']}),
            self.data, format='json')
        data = json.loads(response.content)
        self.assertTrue(data['hidden'])


class GuestMessageAPIViewTests(APITestCase):

    def setUp(self):
        self.password = PASSWORD
        self.today = timezone.now().date()
        # Groups
        create._get_groups_and_perms()
        # Hotel / User
        self.hotel = create_hotel()
        self.admin = create_hotel_user(
            hotel=self.hotel,
            username='admin',
            group='hotel_admin'
        )
        # Guest
        self.guests = make_guests(hotel=self.hotel)
        self.guest = self.guests[0] #b/c returns a list
        # Messages
        self.messages = make_messages(
            hotel=self.hotel,
            user=self.admin,
            guest=self.guest
            )

        # Hotel2
        self.hotel2 = create_hotel()
        self.admin2 = create_hotel_user(self.hotel2, username='admin2', group='hotel_admin')
        self.guests2 = make_guests(hotel=self.hotel2)
        self.guest2 = self.guests2[0]
        self.messages = make_messages(
            hotel=self.hotel2,
            user=self.admin2,
            guest=self.guest2
            )

        # Login
        self.client.login(username=self.admin.username, password=self.password)

    def tearDown(self):
        self.client.logout()

    def test_create(self):
        self.assertEqual(Guest.objects.count(), 20)
        self.assertEqual(Guest.objects.filter(hotel=self.hotel).count(), 10)

    ### GuestMessageListAPIView

    def test_list(self):
        response = self.client.get(reverse('concierge:api_guest_messages'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 10)
        # Confirm all Guests belong to the User's Hotel
        for d in data:
            guest = Guest.objects.get(id=d['id'])
            self.assertEqual(guest.hotel, self.admin.profile.hotel)

    ### GuestMessageRetrieveAPIView

    def test_detail(self):
        guest = Guest.objects.filter(hotel=self.hotel).first()
        response = self.client.get(reverse('concierge:api_guest_messages', kwargs={'pk':guest.pk}))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['id'], guest.id)


class GuestAPITests(APITestCase):

    def setUp(self):
        self.password = PASSWORD
        self.today = timezone.now().date()
        # Groups
        create._get_groups_and_perms()
        # Hotel / User
        self.hotel = create_hotel()
        self.admin = create_hotel_user(
            hotel=self.hotel,
            username='admin',
            group='hotel_admin'
        )
        # Guest
        self.guests = make_guests(hotel=self.hotel)
        self.guest = self.guests[0] #b/c returns a list
        # Messages
        self.messages = make_messages(
            hotel=self.hotel,
            user=self.admin,
            guest=self.guest
            )

        # Hotel2
        self.hotel2 = create_hotel()
        self.admin2 = create_hotel_user(self.hotel2, username='admin2', group='hotel_admin')
        self.guests2 = make_guests(hotel=self.hotel2)
        self.guest2 = self.guests2[0]
        self.messages = make_messages(
            hotel=self.hotel2,
            user=self.admin2,
            guest=self.guest2
            )

        self.data = {
            'name': 'mike',
            'room_number': '123',
            'phone_number': settings.DEFAULT_TO_PH_2,
            'messages': []
        }

        # Login
        self.client.login(username=self.admin.username, password=self.password)

    def tearDown(self):
        self.client.logout()

    ### GuestListCreateAPIView

    def test_list(self):
        response = self.client.get(reverse('concierge:api_guests'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        for d in data:
            guest = Guest.objects.get(id=d['id'])
            self.assertEqual(guest.hotel, self.admin.profile.hotel)

    def test_create(self):
        response = self.client.post(reverse('concierge:api_guests'), self.data, format='json')
        self.assertEqual(response.status_code, 201)

    ### GuestRetrieveUpdateAPIView

    def test_get(self):
        response = self.client.get(reverse('concierge:api_guests', kwargs={'pk': self.guest.pk}))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['id'], self.guest.id)

    def test_get_other_hotel_guest(self):
        guest = Guest.objects.exclude(hotel=self.hotel).first()
        self.assertIsInstance(guest, Guest)
        response = self.client.get(reverse('concierge:api_guests', kwargs={'pk': guest.pk}))
        self.assertEqual(response.status_code, 403)

    def test_update(self):
        self.data = serializers.GuestListSerializer(self.guest).data
        self.data.update({'name': 'changed'})
        response = self.client.get(reverse('concierge:api_guests', kwargs={'pk': self.guest.pk}),
            self.data, format='json')
        self.assertEqual(response.status_code, 200)


class ReplyAPITests(APITestCase):

    fixtures = ['reply.json']

    def setUp(self):
        self.hotel = create_hotel()
        create._get_groups_and_perms()
        self.admin = create_hotel_user(hotel=self.hotel, username='admin', group='hotel_admin')
        # Hotel Reply
        self.reply = mommy.make(Reply, hotel=self.hotel, letter="A")
        # Hotel Reply Serialized
        serializer = serializers.ReplySerializer(self.reply)
        self.data = serializer.data
        # Hotel 2
        self.hotel_2 = create_hotel()
        self.reply_2 = mommy.make(Reply, hotel=self.hotel_2, letter="A")
        # Login
        self.client.login(username=self.admin.username, password=PASSWORD)

    def tearDown(self):
        self.client.logout()

    def test_list(self):
        response = self.client.get("/api/reply/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertTrue(len(data) > 0) # system Reply fixtures returned

    def test_fields(self):
        response = self.client.get("/api/reply/")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        reply = data[0]
        reply["id"]
        reply["hotel"]
        reply["message"]
        reply["desc"]

    def test_list_only_system_or_hotel(self):
        response = self.client.get("/api/reply/")
        data = json.loads(response.content)
        # Hotel Reply
        self.assertIn(self.reply.id, [x['id'] for x in data])
        # System Reply
        sys_reply = Reply.objects.filter(hotel__isnull=True).first()
        self.assertIn(sys_reply.id, [x['id'] for x in data])
        # Other Hotel Reply
        self.assertNotIn(self.reply_2.id, [x['id'] for x in data])

    def test_get(self):
        response = self.client.get("/api/reply/{}/".format(self.reply.id))
        data = json.loads(response.content)
        self.assertEqual(data['message'], self.reply.message)

    def test_get_other_hotels_reply(self):
        response = self.client.get("/api/reply/{}/".format(self.reply_2.id))
        self.assertEqual(response.status_code, 404)

    def test_create(self):
        data = {
            "hotel": self.hotel.id,
            "letter": "Z",
            "message": "foo",
            "desc": "bar"
        }
        response = self.client.post("/api/reply/", data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_update(self):
        self.data["message"] = "foo"
        response = self.client.put("/api/reply/{}/".format(self.reply.id),
            self.data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.data["message"], Reply.objects.get(id=self.reply.id).message)

    # tests: ``from utils.mixins import DestroyModelMixin``
    def test_delete(self):
        response = self.client.delete("/api/reply/{}/".format(self.reply.id),
            {'override':True}, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Reply.objects.filter(id=self.reply.id).exists())

    def test_delete_other_hotel_reply_fails(self):
        response = self.client.delete("/api/reply/{}/".format(self.reply_2.id))
        self.assertEqual(response.status_code, 404)

    def test_get_queryset(self):
        response = self.client.get('/api/reply/?id={}'.format(self.reply.id))
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)

    def test_get_queryset_hotel(self):
        response = self.client.get('/api/reply/?hotel={}'.format(self.hotel.id))
        data = json.loads(response.content)
        self.assertEqual(
            len(data),
            Reply.objects.filter(hotel=self.hotel).count()
        )

    def test_get_queryset_system_reply_only(self):
        response = self.client.get('/api/reply/?hotel__isnull=True')
        data = json.loads(response.content)
        self.assertEqual(
            len(data),
            Reply.objects.filter(hotel__isnull=True).count()
        )

    ### detail_route / list_route

    def test_all_hotel_letters(self):
        response = self.client.get("/api/reply/hotel-letters/")
        data = json.loads(response.content)
        self.assertEqual(
            len(data),
            len([x[0] for x in REPLY_LETTERS 
                      if x[0] not in settings.RESERVED_REPLY_LETTERS])
        )
        self.assertNotIn(settings.RESERVED_REPLY_LETTERS[0], data)


class TriggerTypeTests(APITestCase):

    def setUp(self):
        self.hotel = create_hotel()
        create._get_groups_and_perms()
        self.admin = create_hotel_user(hotel=self.hotel, username='admin', group='hotel_admin')
        # TriggerType
        self.trigger_type = mommy.make(TriggerType)
        # Login
        self.client.login(username=self.admin.username, password=PASSWORD)

    def tearDown(self):
        self.client.logout()

    def test_detail(self):
        response = self.client.get('/api/trigger-type/{}/'.format(self.trigger_type.id))
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)


class TriggerTests(APITestCase):

    def setUp(self):
        self.hotel = create_hotel()
        create._get_groups_and_perms()
        self.admin = create_hotel_user(hotel=self.hotel, username='admin', group='hotel_admin')
        # Trigger
        self.trigger_type = mommy.make(TriggerType)
        self.trigger = mommy.make(Trigger, type=self.trigger_type, hotel=self.hotel)
        # Login
        self.client.login(username=self.admin.username, password=PASSWORD)

    def tearDown(self):
        self.client.logout()

    def test_list(self):
        response = self.client.get('/api/trigger/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 1)

    def test_detail_type(self):
        response = self.client.get('/api/trigger/{}/'.format(self.trigger.id))
        data = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.trigger.type.id,
            data['type']['id']
        )

    def test_detail_reply(self):
        response = self.client.get('/api/trigger/{}/'.format(self.trigger.id))
        data = json.loads(response.content)
        self.assertEqual(
            self.trigger.reply.letter,
            data['reply']['letter']
        )
