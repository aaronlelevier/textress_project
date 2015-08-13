from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group

import stripe

from main.models import Hotel, UserProfile, Subaccount
from main.tests.factory import (CREATE_USER_DICT, CREATE_HOTEL_DICT,
    create_hotel, create_hotel_user)
from utils import create
from utils.messages import dj_messages


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_admin():
    "`hotel_admin` Group Obj needs to be pre created for this to work."
    admin = User.objects.create(username="Admin", email="pyaaron@gmail.com",
        password="1234", is_superuser=True, is_staff=True)
    admin_group = Group.objects.get(name="hotel_admin")
    admin.groups.add(admin_group)
    admin.set_password("1234")
    admin.save()
    return admin


class RegistrationTests(TestCase):

    # fixtures = ['main.json', 'payment.json']

    def setUp(self):
        create._get_groups_and_perms()

        # Login Credentials
        self.username = 'test'
        self.password = '1234'

    ### SUCCESSFUL REGISTRATION TESTs ###

    def test_register_step1(self):
        # Dave creates a User
        response = self.client.post(reverse('main:register_step1'),
            CREATE_USER_DICT, follow=True)

        self.assertRedirects(response, reverse('main:register_step2'))

        user = User.objects.get(username=self.username)
        assert isinstance(user, User)
        assert isinstance(user.profile, UserProfile)
        assert user == User.objects.get(groups__name='hotel_admin')

        # after Dave tries to go back and it takes him to the update URL instead
        response = self.client.get(reverse('main:register_step1'), follow=True)
        self.assertRedirects(response, reverse('main:register_step1_update', kwargs={'pk': user.pk}))

    def test_register_step2(self):
        # Step 1
        # assert logged in and can access "register step2 form"
        response = self.client.post(reverse('main:register_step1'),
            CREATE_USER_DICT)
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('main:register_step2'))
        self.assertEqual(response.status_code, 200)

        # Step 2
        # Dave creates a Hotel
        response = self.client.post(reverse('main:register_step2'),
            CREATE_HOTEL_DICT, follow=True)
        self.assertRedirects(response, reverse('register_step3'))

        # User set as Admin and Hotel properly linked
        hotel = Hotel.objects.get(name=CREATE_HOTEL_DICT['name'])
        updated_user = User.objects.get(username=self.username)
        self.assertEqual(hotel.admin_id, updated_user.id)
        self.assertEqual(updated_user.profile.hotel, hotel)

        # Dave tries to go back and Edit the Hotel and it takes him to the UpdateView
        response = self.client.get(reverse('main:register_step2'), follow=True)
        self.assertRedirects(response, reverse('main:register_step2_update', kwargs={'pk': hotel.pk}))


class HotelViewTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        
        # Login Credentials
        self.username = 'test'
        self.password = '1234'

        # requires Admin User and Hotel 
        # Dave
        response = self.client.post(reverse('main:register_step1'),
            CREATE_USER_DICT)
        # Hotel
        response = self.client.post(reverse('main:register_step2'),
            CREATE_HOTEL_DICT)
        self.user = User.objects.first()
        self.hotel = self.user.profile.hotel

    def test_update_get(self):
        self.client.login(username=self.username, password=self.password)
        # Dave can access HotelUpdateView
        response = self.client.get(reverse('main:hotel_update', kwargs={'pk': self.hotel.pk}))
        self.assertEqual(response.status_code, 200)
        
        # Logged in Message
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        self.assertEqual(str(m[0]), "You are now logged in")

    def test_update_get_other_user(self):
        # normal Hotel Users should not be able to access this View.
        self.client.logout()
        # User
        user = create_hotel_user(self.hotel)
        self.assertEqual(self.hotel, user.profile.hotel)
        # Login
        self.client.login(username=user.username, password=self.password)
        # View
        response = self.client.get(reverse('main:hotel_update', kwargs={'pk': self.hotel.pk}))
        self.assertEqual(response.status_code, 302)

    def test_update_get_other_manager(self):
        # Managers should not be able to access this View.
        self.client.logout()
        # User
        user = create_hotel_user(self.hotel, group='hotel_manager')
        self.assertEqual(self.hotel, user.profile.hotel)
        # Login
        self.client.login(username=user.username, password=self.password)
        # View
        response = self.client.get(reverse('main:hotel_update', kwargs={'pk': self.hotel.pk}))
        self.assertEqual(response.status_code, 302)

    def test_update_post(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.post(reverse('main:hotel_update', kwargs={'pk': self.hotel.pk}))

        # Dave changes his street address, and the change is saved in the DB
        CREATE_HOTEL_DICT['address_line1'] = '123 My New Street Name' 
        response = self.client.post(reverse('main:hotel_update', kwargs={'pk': self.hotel.pk}),
            CREATE_HOTEL_DICT, follow=True)
        # hotel info updated
        self.assertRedirects(response, reverse('main:hotel_update', kwargs={'pk': self.hotel.pk}))
        updated_hotel = Hotel.objects.get(admin_id=self.user.pk)
        self.assertNotEqual(self.hotel.address_line1, updated_hotel.address_line1)
        
        # success message
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        self.assertEqual(str(m[0]), dj_messages['hotel_updated'])


class UserUpdateTest(TestCase):

    def setUp(self):
        # create a User through the registration process
        create._get_groups_and_perms()
        # Login Credentials
        self.username = 'test'
        self.password = '1234'
        response = self.client.post(reverse('main:register_step1'),
            CREATE_USER_DICT)

    def test_update(self):
        user = User.objects.first()
        assert isinstance(user, User)


class UserViewTests(TestCase):

    def setUp(self):
        self.password = '1234'
        self.hotel = create_hotel()

        # create "Hotel Manager" Group
        create._get_groups_and_perms()

        # Users
        self.mgr = create_hotel_user(hotel=self.hotel, username='mgr', group='hotel_manager')
        self.user = create_hotel_user(hotel=self.hotel, username='user')

    def test_create(self):
        # both have a hotel attr
        assert isinstance(self.user.profile.hotel, Hotel)
        assert isinstance(self.mgr.profile.hotel, Hotel)

        # mgr is a "hotel_manager"
        mgr_group = Group.objects.get(name="hotel_manager")
        assert mgr_group in self.mgr.groups.all()

    def test_update(self):
        # User can update
        fname = self.user.first_name

        # Mgr can't Access
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:user_update', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 403)

        # Login n Get
        self.client.logout()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('main:user_update', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)

        # Post
        response = self.client.post(reverse('main:user_update', kwargs={'pk': self.user.pk}),
            {'first_name': 'new name', 'last_name': self.user.last_name, 'email': self.user.email},
            follow=True)
        # User updated n redirects
        updated_user = User.objects.get(username=self.user.username)
        self.assertNotEqual(fname, updated_user.first_name)
        self.assertRedirects(response, reverse('account'))

    def test_user_detail(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('main:user_detail', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)


class ManageUsersTests(TestCase):

    def setUp(self):
        self.password = '1234'
        self.hotel = create_hotel()

        # create Groups
        create._get_groups_and_perms()

        # Users
        self.admin = create_hotel_user(hotel=self.hotel, username='admin', group='hotel_admin')
        self.mgr = create_hotel_user(hotel=self.hotel, username='mgr', group='hotel_manager')
        self.user = create_hotel_user(hotel=self.hotel, username='user')

    def test_list(self):
        # mgr can access
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:manage_user_list'))
        self.assertEqual(response.status_code, 200)

        # normal user cannot
        self.client.logout()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('main:manage_user_list'))
        self.assertEqual(response.status_code, 302)

    ### CREATE USER ###

    def test_create_user_get(self):
        # mgr can access
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:create_user'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['headline'])

        # normal user cannot
        self.client.logout()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('main:create_user'))
        self.assertEqual(response.status_code, 302)

    def test_create_user_post(self):
        # mgr can access
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.post(reverse('main:create_user'),
            {'first_name': 'fname', 'last_name': 'lname',
            'email': settings.DEFAULT_FROM_EMAIL, 'username': 'test_create',
            'password1': self.password, 'password2': self.password},
            follow=True)

        # new User created, redirects to "Manage Users List"
        new_user = User.objects.get(username='test_create')
        assert isinstance(new_user, User)
        self.assertRedirects(response, reverse('main:manage_user_list'))

    ### CREATE MGR ###

    def test_create_mgr_get(self):
        # mgr can access
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:create_manager'))
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(response.context['headline'])

        # normal user cannot
        self.client.logout()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('main:create_manager'))
        self.assertEqual(response.status_code, 302)

    def test_create_mgr_post(self):
        # mgr can access
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.post(reverse('main:create_manager'),
            {'first_name': 'fname', 'last_name': 'lname',
            'email': settings.DEFAULT_FROM_EMAIL, 'username': 'test_create_mgr',
            'password1': self.password, 'password2': self.password},
            follow=True)

        # new MGR created, is part of Mgr Group, redirects to "Manage Users List"
        new_user = User.objects.get(username='test_create_mgr')
        assert isinstance(new_user, User)
        assert Group.objects.get(name="hotel_manager") in new_user.groups.all()
        self.assertRedirects(response, reverse('main:manage_user_list'))


    # NEXT: Add tests for "Update" from Mgr point of view

    def test_update(self):
        # User can update
        fname = self.user.first_name

        # User can't Access
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('main:manage_user_update', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 302)

        # Mgr Only can Access
        self.client.logout()
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:manage_user_update', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)

        # Post
        response = self.client.post(reverse('main:manage_user_update', kwargs={'pk': self.user.pk}),
            {'first_name': 'mgr new name', 'last_name': self.user.last_name, 'email': self.user.email},
            follow=True)
        # User updated n redirects
        updated_user = User.objects.get(username=self.user.username)
        assert fname != updated_user.first_name
        self.assertRedirects(response, reverse('main:manage_user_list'))

    def test_delete(self):
        # get
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:manage_user_delete', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)
        # delete => only hides
        self.assertFalse(self.user.profile.hidden)
        response = self.client.post(reverse('main:manage_user_delete', kwargs={'pk': self.user.pk}), follow=True)
        self.assertRedirects(response, reverse('main:manage_user_list'))
        self.user = User.objects.get(pk=self.user.pk)
        self.assertTrue(self.user.profile.hidden)

    def test_delete_admin(self):
        # UserProfile.hide() for an "Admin" will raise a ValidationError b/c can't hide Admin.
        self.client.login(username=self.mgr.username, password=self.password)
        with self.assertRaises(ValidationError):
            response = self.client.post(reverse('main:manage_user_delete',
                kwargs={'pk': self.admin.pk}), follow=True)
