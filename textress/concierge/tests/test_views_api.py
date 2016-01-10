import json

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import timezone

from model_mommy import mommy
from rest_framework.test import APITestCase

from concierge import serializers
from concierge.models import Reply, REPLY_LETTERS, TriggerType, Trigger, Guest, Message
from concierge.tests.factory import make_guests, make_messages
from main.models import Hotel
from main.tests.factory import create_hotel, create_user, create_hotel_user, PASSWORD
from utils import create


class MessagAPIViewTests(APITestCase):

    def setUp(self):
        # Groups
        create._get_groups_and_perms()
        # User
        self.hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, group='hotel_admin')
        self.manager = create_hotel_user(self.hotel, group='hotel_manager')
        self.user = create_hotel_user(self.hotel)
        # Guest
        self.guest = make_guests(hotel=self.hotel, number=1)[0] #b/c returns a list
        # Messages
        self.messages = make_messages(
            hotel=self.hotel,
            user=self.admin,
            guest=self.guest
            )

        msg = Message.objects.filter(hotel=self.hotel).first()
        serializer = serializers.MessageRetrieveSerializer(msg)
        self.data = serializer.data

        # Hotel2
        self.hotel2 = create_hotel()
        self.admin2 = create_hotel_user(self.hotel2, username='admin2', group='hotel_admin')
        self.guest2 = make_guests(hotel=self.hotel2, number=1)[0]
        self.messages2 = make_messages(
            hotel=self.hotel2,
            user=self.admin2,
            guest=self.guest2
            )

        # Login
        self.client.login(username=self.admin.username, password=PASSWORD)

    def tearDown(self):
        self.client.logout()

    def test_setup_data(self):
        self.assertEqual(Message.objects.count(), 20)
        self.assertEqual(Message.objects.filter(hotel=self.hotel).count(), 10)

    # permissions - by User Type

    def test_manager_access(self):
        self.client.logout()
        self.client.login(username=self.manager.username, password=PASSWORD)
        response = self.client.get('/api/messages/')
        self.assertEqual(response.status_code, 200)

    def test_user_access(self):
        self.client.logout()
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get('/api/messages/')
        self.assertEqual(response.status_code, 200)

    ### MessageListCreateAPIView

    def test_list(self):
        response = self.client.get('/api/messages/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 10)

    def test_list_no_other_hotel_messages(self):
        response = self.client.get('/api/messages/')
        data = json.loads(response.content)
        for d in data:
            msg = Message.objects.get(id=d['id'])
            self.assertEqual(msg.hotel, self.admin.profile.hotel)

    def test_list_no_deleted(self):
        response = self.client.get('/api/messages/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        message = Message.objects.get(id=data[0]['id'])
        message.delete()
        self.assertTrue(message.hidden)
        # Deleted
        response = self.client.get('/api/messages/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertNotIn(
            message.id,
            [x['id'] for x in data]
        )

    # create

    def test_create(self):
        data = {
            'top_ph': self.guest.phone_number,
            'guest': str(self.guest.id),
            'user': str(self.admin.id),
            'body': 'hi'
        }
        response = self.client.post('/api/messages/', data, format='json')
        self.assertEqual(response.status_code, 201)

    ### MessageRetrieveAPIView

    def test_detail(self):
        message = Message.objects.filter(hotel=self.hotel).first()
        response = self.client.get('/api/messages/{}/'.format(message.pk))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['id'], message.pk)

    def test_detail_other_hotel_messages(self):
        message = Message.objects.exclude(hotel=self.hotel).first()
        self.assertIsInstance(message, Message)
        response = self.client.get('/api/messages/{}/'.format(message.pk))
        self.assertEqual(response.status_code, 403)

    def test_detail_put(self):
        self.assertFalse(self.data['hidden'])
        self.data['hidden'] = True
        response = self.client.put('/api/messages/{}/'.format(self.data['id']),
            self.data, format='json')
        data = json.loads(response.content)
        self.assertTrue(data['hidden'])

    def test_delete(self):
        message = self.messages[0]
        self.assertEqual(self.admin.profile.hotel, message.hotel)
        response = self.client.post('/api/messages/{}/'.format(message.pk),
            {'override': True}, format='json')
        self.assertEqual(response.status_code, 405)


class GuestMessageAPIViewTests(APITestCase):

    def setUp(self):
        self.today = timezone.localtime(timezone.now()).date()
        # Groups
        create._get_groups_and_perms()
        # Hotel / User
        self.hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, group='hotel_admin')
        self.manager = create_hotel_user(self.hotel, group='hotel_manager')
        self.user = create_hotel_user(self.hotel)
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
        self.client.login(username=self.admin.username, password=PASSWORD)

    def tearDown(self):
        self.client.logout()

    def test_setup_data(self):
        self.assertEqual(Guest.objects.count(), 20)
        self.assertEqual(Guest.objects.filter(hotel=self.hotel).count(), 10)

    # permissions - by User Type

    def test_manager_access(self):
        self.client.logout()
        self.client.login(username=self.manager.username, password=PASSWORD)
        response = self.client.get('/api/guest-messages/')
        self.assertEqual(response.status_code, 200)

    def test_user_access(self):
        self.client.logout()
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get('/api/guest-messages/')
        self.assertEqual(response.status_code, 200)

    ### GuestMessageListAPIView

    def test_list(self):
        response = self.client.get('/api/guest-messages/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(len(data), 10)
        # Confirm all Guests belong to the User's Hotel
        for d in data:
            guest = Guest.objects.get(id=d['id'])
            self.assertEqual(guest.hotel, self.admin.profile.hotel)

    def test_list_no_deleted_guests(self):
        response = self.client.get('/api/guest-messages/')
        data = json.loads(response.content)
        self.assertIn(
            self.guest.id,
            [x['id'] for x in data]
        )
        # Delete
        self.guest.delete()
        self.assertTrue(self.guest.hidden)
        response = self.client.get('/api/guest-messages/')
        data = json.loads(response.content)
        self.assertNotIn(
            self.guest.id,
            [x['id'] for x in data]
        )

    ### GuestMessageRetrieveAPIView

    def test_detail(self):
        guest = Guest.objects.filter(hotel=self.hotel).first()
        response = self.client.get('/api/guest-messages/{}/'.format(guest.pk))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['id'], guest.id)


class GuestAPIViewTests(APITestCase):

    def setUp(self):
        self.today = timezone.localtime(timezone.now()).date()
        # Groups
        create._get_groups_and_perms()
        # Hotel / User
        self.hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, group='hotel_admin')
        self.manager = create_hotel_user(self.hotel, group='hotel_manager')
        self.user = create_hotel_user(self.hotel)
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
        self.client.login(username=self.admin.username, password=PASSWORD)

    def tearDown(self):
        self.client.logout()

    # permissions - by User Type

    def test_manager_access(self):
        self.client.logout()
        self.client.login(username=self.manager.username, password=PASSWORD)
        response = self.client.get('/api/guests/')
        self.assertEqual(response.status_code, 200)

    def test_user_access(self):
        self.client.logout()
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get('/api/guests/')
        self.assertEqual(response.status_code, 200)

    ### GuestListCreateAPIView

    def test_list(self):
        response = self.client.get('/api/guests/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        for d in data:
            guest = Guest.objects.get(id=d['id'])
            self.assertEqual(guest.hotel, self.admin.profile.hotel)

    def test_detail(self):
        response = self.client.get('/api/guests/{}/'.format(self.guest.pk))
        self.assertEqual(response.status_code, 405)

    def test_list_no_deleted_guests(self):
        response = self.client.get('/api/guests/')
        data = json.loads(response.content)
        self.assertIn(
            self.guest.id,
            [x['id'] for x in data]
        )
        # Delete
        self.guest.delete()
        self.assertTrue(self.guest.hidden)
        response = self.client.get('/api/guests/')
        data = json.loads(response.content)
        self.assertNotIn(
            self.guest.id,
            [x['id'] for x in data]
        )


class ReplyAPIViewTests(APITestCase):

    fixtures = ['reply.json']

    def setUp(self):
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, group='hotel_admin')
        self.manager = create_hotel_user(self.hotel, group='hotel_manager')
        self.user = create_hotel_user(self.hotel)
        # Hotel Reply
        self.reply = mommy.make(Reply, hotel=self.hotel, letter="A")
        # Hotel Reply Serialized
        serializer = serializers.ReplySerializer(self.reply)
        self.data = serializer.data
        # Hotel 2
        self.hotel_2 = create_hotel()
        self.reply_2 = mommy.make(Reply, hotel=self.hotel_2, letter="A")
        # System Reply
        self.system_reply = Reply.objects.get(letter="S")
        # Login
        self.client.login(username=self.admin.username, password=PASSWORD)

    def tearDown(self):
        self.client.logout()

    # permissions - by User Type

    def test_manager_access(self):
        self.client.logout()
        self.client.login(username=self.manager.username, password=PASSWORD)
        response = self.client.get("/api/reply/")
        self.assertEqual(response.status_code, 200)

    def test_user_access(self):
        self.client.logout()
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get("/api/reply/")
        self.assertEqual(response.status_code, 403)

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
        self.assertIn("id", reply)
        self.assertIn("hotel", reply)
        self.assertIn("message", reply)
        self.assertIn("desc", reply)

    def test_list_only_system_or_hotel(self):
        response = self.client.get("/api/reply/")
        data = json.loads(response.content)
        # Hotel Reply
        self.assertIn(self.reply.id, [x['id'] for x in data])
        # System Reply
        self.assertIn(self.system_reply.id, [x['id'] for x in data])
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

    def test_delete__other_hotel_reply_fails(self):
        response = self.client.delete("/api/reply/{}/".format(self.reply_2.id))
        self.assertEqual(response.status_code, 404)

    def test_delete__system_reply_fails(self):
        response = self.client.delete("/api/reply/{}/".format(self.system_reply.id))
        self.assertEqual(response.status_code, 403)

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


class TriggerTypeAPIViewTests(APITestCase):

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

    def test_list(self):
        response = self.client.get('/api/trigger-type/', format='json')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        data = data['results']
        trigger_type = TriggerType.objects.get(id=data[0]['id'])
        
        self.assertEqual(data[0]['name'], trigger_type.name)
        self.assertEqual(data[0]['human_name'], trigger_type.human_name)
        self.assertEqual(data[0]['desc'], trigger_type.desc)

    def test_detail(self):
        response = self.client.get('/api/trigger-type/{}/'.format(self.trigger_type.id))

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        
        self.assertEqual(data['id'], self.trigger_type.id)
        self.assertEqual(data['name'], self.trigger_type.name)
        self.assertEqual(data['human_name'], self.trigger_type.human_name)
        self.assertEqual(data['desc'], self.trigger_type.desc)


    def test_create(self):
        response = self.client.post('/api/trigger-type/', {'foo':'bar'}, format='json')
        self.assertEqual(response.status_code, 405)

    def test_update(self):
        response = self.client.put('/api/trigger-type/{}/'.format(self.trigger_type.id),
            {'foo':'bar'}, format='json')
        self.assertEqual(response.status_code, 405)

    def test_delete(self):
        response = self.client.delete('/api/trigger-type/{}/'.format(self.trigger_type.id))
        
        self.assertEqual(response.status_code, 405)

        self.assertIsNotNone(TriggerType.objects.get(id=self.trigger_type.id))


class TriggerAPIViewTests(APITestCase):

    def setUp(self):
        self.hotel = create_hotel()
        create._get_groups_and_perms()
        self.admin = create_hotel_user(self.hotel, group='hotel_admin')
        self.manager = create_hotel_user(self.hotel, group='hotel_manager')
        self.user = create_hotel_user(self.hotel)
        # Trigger
        self.trigger_type = mommy.make(TriggerType)
        self.trigger = mommy.make(Trigger, type=self.trigger_type, hotel=self.hotel)
        # Login
        self.client.login(username=self.admin.username, password=PASSWORD)

    def tearDown(self):
        self.client.logout()

    # permissions - by User Type

    def test_manager_access(self):
        self.client.logout()
        self.client.login(username=self.manager.username, password=PASSWORD)
        response = self.client.get("/api/reply/")
        self.assertEqual(response.status_code, 200)

    def test_user_access(self):
        self.client.logout()
        self.client.login(username=self.user.username, password=PASSWORD)
        response = self.client.get("/api/reply/")
        self.assertEqual(response.status_code, 403)

    # list

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

class CurrentUserAPIView(APITestCase):

    def setUp(self):
        self.hotel = create_hotel()
        create._get_groups_and_perms()
        self.admin = create_hotel_user(hotel=self.hotel, username='admin', group='hotel_admin')

    def test_logged_in(self):
        self.client.login(username=self.admin.username, password=PASSWORD)
        response = self.client.get('/api/current-user/')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['id'], self.admin.id)
        self.assertEqual(data['hotel_id'], self.admin.profile.hotel.id)

    def test_logged_out(self):
        response = self.client.get('/api/current-user/')
        self.assertEqual(response.status_code, 403)

    def test_no_hotel(self):
        # Delete Hotel
        user, group = create_user()
        # Test 403 w/o a Hotel
        self.client.login(username=user.username, password=PASSWORD)
        response = self.client.get('/api/current-user/')
        self.assertEqual(response.status_code, 403)
