from django.test import TestCase
from django.core.urlresolvers import reverse

from concierge.forms import GuestForm
from concierge.models import Guest, Message
from concierge.tests.factory import make_guests, make_messages
from main.tests.factory import create_hotel, create_hotel_user, PASSWORD
from utils import create
from utils.exceptions import CheckOutDateException
from utils.models import Dates


class GuestViewTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()

        # set User "aaron_test" from fixtures as an attr on this class
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, group='hotel_admin')

        self.guests = make_guests(self.hotel)
        self.guest = self.guests.first()

        self.guest_create_data = {
            'hotel':self.user.profile.hotel,
            'name': 'Test Guest',
            'room_number': create._generate_int(5),
            'phone_number': create._generate_ph(),
            'check_in': create._generate_date(),
            'check_out': create._generate_date()
        }

        # Login
        self.client.login(username=self.user.username, password=PASSWORD)

    def tearDown(self):
        self.client.logout()

    # list

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

    # detail

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

    # create

    def test_create(self):
        [g.delete(override=True) for g in Guest.objects.all()]
        self.assertEqual(Guest.objects.count(), 0)

        # Login n Create a Guest
        response = self.client.post(reverse('concierge:guest_create'),
            self.guest_create_data, follow=True)

        # Now 1 guest
        guest = Guest.objects.first()
        self.assertIsInstance(guest, Guest)
        self.assertRedirects(response, reverse('concierge:guest_detail', kwargs={'pk':guest.pk}))

    def test_create__past_date_check_in(self):
        dates = Dates()
        self.guest_create_data['check_in'] = dates._yesterday
        self.guest_create_data['check_out'] = dates._yesterday
        [g.delete(override=True) for g in Guest.objects.all()]

        # Login n Create a Guest
        response = self.client.post(reverse('concierge:guest_create'),
            self.guest_create_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'check_in', GuestForm.error_messages['check_in_past_date'])

    def test_validate_phone_in_use(self):
        [g.delete(override=True) for g in Guest.objects.all()]

        # Login n Create a Guest
        response = self.client.post(reverse('concierge:guest_create'),
            self.guest_create_data, follow=True)

        # Now 1 guest
        guest = Guest.objects.first()
        self.assertIsInstance(guest, Guest)
        self.assertRedirects(response, reverse('concierge:guest_detail', kwargs={'pk':guest.pk}))

        # Trying to creat a Guest w/ the same Phone Number will fail
        response = self.client.post(reverse('concierge:guest_create'),
            self.guest_create_data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'phone_number', GuestForm.error_messages['number_in_use'])

    def test_validate_phone_in_use_deleted_guest(self):
        # Deleted Guests should not raise errors because they are not active, so their
        # Phone Number is free to be used
        [g.delete(override=True) for g in Guest.objects.all()]

        response = self.client.post(reverse('concierge:guest_create'),
            self.guest_create_data, follow=True)
        guest = Guest.objects.first()
        self.assertIsInstance(guest, Guest)
        self.assertRedirects(response, reverse('concierge:guest_detail', kwargs={'pk':guest.pk}))

        guest.delete()
        self.assertTrue(guest.hidden)

        # Should succeed b/c PH # not in use
        init_count = Guest.objects.count()
        response = self.client.post(reverse('concierge:guest_create'),
            self.guest_create_data)
        post_count = Guest.objects.count()
        self.assertEqual(init_count+1, post_count)

    def test_validate_check_in_out(self):
        """
        `check_out` cannot be before the `check_in`
        """
        dates = Dates()
        self.guest_create_data['check_out'] = dates._yesterday

        response = self.client.post(reverse('concierge:guest_create'),
            self.guest_create_data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'check_out',
            GuestForm.error_messages['check_out_before_check_in'])

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
