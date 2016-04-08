from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from model_mommy import mommy

from concierge.forms import GuestForm
from concierge.models import Guest, Message, Trigger, TriggerType, Reply
from concierge.tasks import create_hotel_default_buld_send_welcome
from concierge.tests.factory import make_guests, make_messages
from main.tests.factory import create_hotel, create_hotel_user, PASSWORD
from utils import create
from utils.models import Dates


class SendWelcomeTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, group='hotel_admin')
        self.guests = make_guests(self.hotel)
        self.guest = self.guests.first()
        # Login
        self.client.login(username=self.user.username, password=PASSWORD)

    def test_get(self):
        response = self.client.get(reverse('concierge:send_welcome'))
        self.assertEqual(response.status_code, 200)

    def test_context_welcome_message__configured(self):
        create_hotel_default_buld_send_welcome(self.hotel.id)
        msg = Trigger.objects.get_welcome_message(hotel=self.hotel)
        self.assertEqual(msg, settings.DEFAULT_REPLY_BULK_SEND_WELCOME_MSG)

        response = self.client.get(reverse('concierge:send_welcome'))

        self.assertEqual(response.context['welcome_message'], msg)
        self.assertIn(msg, response.content)

    def test_context_welcome_message__not_configured(self):
        msg = Trigger.objects.get_welcome_message(hotel=self.hotel)
        self.assertEqual(msg, settings.WELCOME_MSG_NOT_CONFIGURED)

        response = self.client.get(reverse('concierge:send_welcome'))

        self.assertEqual(response.context['welcome_message'], msg)
        self.assertIn(msg, response.content)


class GuestViewTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()

        # set User "aaron_test" from fixtures as an attr on this class
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, group='hotel_admin')

        self.guests = make_guests(self.hotel)
        self.guest = self.guests.first()

        self.guest_create_data = {
            'hotel':self.hotel,
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
        response = self.client.get(reverse('concierge:guest_list'), follow=True)

        self.assertRedirects(response, "{}?next={}".format(reverse('login'),
            reverse('concierge:guest_list')))

    def test_list_ok(self):
        # Dave now tries Logged-In        
        response = self.client.get(reverse('concierge:guest_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['object_list'])

    def test_list_content(self):
        response = self.client.get(reverse('concierge:guest_list'))

        self.assertEqual( "Guest List", response.context['headline'])
        self.assertIn(
            '<i class="clip-plus-circle"> <strong>Add a Guest</strong></i>',
            response.content
        )

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
        self.assertEqual(guest.hotel, self.hotel)
        self.assertRedirects(response, reverse('concierge:guest_list'))

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
        self.assertRedirects(response, reverse('concierge:guest_list'))

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
        self.assertRedirects(response, reverse('concierge:guest_list'))

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

    # update

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

    # delete

    def test_delete(self):
        guest = Guest.objects.first()
        self.assertTrue(isinstance(guest, Guest))
        self.assertFalse(guest.hidden)

        # Hide
        response = self.client.post(reverse('concierge:guest_delete',
            kwargs={'pk': guest.pk}), {}, follow=True)

        self.assertRedirects(response, reverse('concierge:guest_list'))
        # hide guest worked
        updated_guest = Guest.objects.get(pk=guest.pk)
        self.assertTrue(updated_guest.hidden)

    ### ReplyView

    def test_replies(self):
        response = self.client.get(reverse('concierge:replies'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['headline'], "Auto Replies")
        self.assertEqual(response.context['headline_small'], "& Automatic Messaging")


    def test_replies__logged_out(self):
        self.client.logout()

        response = self.client.get(reverse('concierge:replies'), follow=True)

        self.assertRedirects(response, "{}?next={}".format(reverse('login'),
            reverse('concierge:replies')))


class GuestViewTriggerReplyTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()

        # set User "aaron_test" from fixtures as an attr on this class
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, group='hotel_admin')

        self.guests = make_guests(self.hotel)
        self.guest = self.guests.first()

        self.guest_create_data = {
            'hotel':self.hotel,
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

    # create

    def test_create__no_triggered_check_in_msg(self):
        [g.delete(override=True) for g in Guest.objects.all()]
        self.assertEqual(Guest.objects.count(), 0)
        self.assertEqual(Message.objects.count(), 0)

        # Login n Create a Guest
        response = self.client.post(reverse('concierge:guest_create'),
            self.guest_create_data, follow=True)

        self.assertEqual(Message.objects.count(), 0)

    def test_create__check_in_msg(self):
        # check-in
        check_in_letter = "W"
        check_in_message = "Welcome"
        check_in_trigger_name = "check_in"
        check_in_reply = mommy.make(Reply, hotel=self.hotel, letter=check_in_letter,
            message=check_in_message)
        check_in_trigger_type = mommy.make(TriggerType, name=check_in_trigger_name)
        check_in_trigger = mommy.make(Trigger, hotel=self.hotel, type=check_in_trigger_type,
            reply=check_in_reply)
        # Guest / Message setup
        [g.delete(override=True) for g in Guest.objects.all()]
        self.assertEqual(Guest.objects.count(), 0)
        self.assertEqual(Message.objects.count(), 0)

        # Login n Create a Guest
        response = self.client.post(reverse('concierge:guest_create'),
            self.guest_create_data, follow=True)

        self.assertEqual(Message.objects.count(), 1)
        msg = Message.objects.first()
        self.assertEqual(Guest.objects.count(), 1)
        self.assertEqual(msg.guest, Guest.objects.first())
        self.assertEqual(msg.body, check_in_message)

    # delete

    def test_delete__no_triggered_check_out_msg(self):
        guest = Guest.objects.first()
        self.assertEqual(Message.objects.count(), 0)

        response = self.client.post(reverse('concierge:guest_delete',
            kwargs={'pk': guest.pk}), {}, follow=True)

        self.assertEqual(Message.objects.count(), 0)

    def test_delete__check_out_msg(self):
        # check-out
        check_out_letter = "T"
        check_out_message = "Thank you"
        check_out_trigger_name = "check_out"
        check_out_reply = mommy.make(Reply, hotel=self.hotel, letter=check_out_letter,
            message=check_out_message)
        check_out_trigger_type = mommy.make(TriggerType, name=check_out_trigger_name)
        check_out_trigger = mommy.make(Trigger, hotel=self.hotel, type=check_out_trigger_type,
            reply=check_out_reply)
        # Guest / Message setup
        guest = Guest.objects.first()
        self.assertEqual(Message.objects.count(), 0)

        response = self.client.post(reverse('concierge:guest_delete',
            kwargs={'pk': guest.pk}), {}, follow=True)

        self.assertEqual(Message.objects.count(), 1)
        msg = Message.objects.first()
        self.assertEqual(msg.guest, guest)
        self.assertEqual(msg.body, check_out_message)
