from django.test import TestCase
from django.core.urlresolvers import reverse

from concierge.models import Guest, Message
from concierge.tests.factory import make_guests, make_messages
from main.tests.factory import create_hotel, create_hotel_user, PASSWORD
from utils import create


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
        make_messages(
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
        updated_guest = Guest.objects_all.get(pk=guest.pk)
        self.assertTrue(updated_guest.hidden)

    ### ReplyView

    def test_replies(self):
        response = self.client.get(reverse('concierge:replies'))
        self.assertEqual(response.status_code, 200)
