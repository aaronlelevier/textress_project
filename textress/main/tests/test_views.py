from django.conf import settings
from django.test import TestCase, TransactionTestCase
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User, Group

import stripe

from main.forms import UserCreateForm, UserUpdateForm, HotelCreateForm
from main.models import Hotel, UserProfile, Subaccount
from main.tests.factory import (CREATE_USER_DICT, CREATE_HOTEL_DICT, PASSWORD,
    create_hotel, create_user, create_hotel_user)
from utils import create, dj_messages, login_messages, ph_formatter


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


class RegistrationTests(TransactionTestCase):

    def setUp(self):
        create._get_groups_and_perms()

        # Login Credentials
        self.username = 'test'
        self.password = '1234'

    # Step 1

    def test_register_step1_get(self):
        # initially logged-out
        self.assertNotIn('_auth_user_id', self.client.session)
        response = self.client.get(reverse('main:register_step1'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], UserCreateForm)

    def test_register_step1(self):
        # Dave creates a User
        response = self.client.post(reverse('main:register_step1'),
            CREATE_USER_DICT, follow=True)

        self.assertRedirects(response, reverse('main:register_step2'))

        user = User.objects.get(username=self.username)
        self.assertIsInstance(user, User)
        self.assertIsInstance(user.profile, UserProfile)
        group = Group.objects.get(name='hotel_admin')
        self.assertIn(group, user.groups.all())

        # Now logged-in
        self.assertIn('_auth_user_id', self.client.session)
        # Logged in Message
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        self.assertEqual(str(m[0]), login_messages['now_logged_in'])

    def test_register_step1_update_info(self):
        # after Dave tries to go back and it takes him to the update URL instead
        user, group = create_user(username=self.username, group="hotel_admin")
        self.client.login(username=user.username, password=PASSWORD)

        response = self.client.get(reverse('main:register_step1'), follow=True)
        self.assertRedirects(response, reverse('main:register_step1_update', kwargs={'pk': user.pk}))
        self.assertIsInstance(response.context['form'], UserUpdateForm)

    def test_register_step1_clean_username(self):
        create_user(username=CREATE_USER_DICT['username'])
        response = self.client.post(reverse('main:register_step1'), CREATE_USER_DICT)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'username',
            UserCreateForm.error_messages['duplicate_username'])

    def test_register_step1_clean_password2(self):
        CREATE_USER_DICT['password2'] = create._generate_name()
        response = self.client.post(reverse('main:register_step1'), CREATE_USER_DICT)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'password2',
            UserCreateForm.error_messages['password_mismatch'])

    # Step 2

    def test_register_step2_get(self):
        user, group = create_user(username=self.username, group="hotel_admin")
        self.client.login(username=user.username, password=PASSWORD)
        response = self.client.get(reverse('main:register_step2'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], HotelCreateForm)

    def test_register_step2(self):
        # Step 1
        user, group = create_user(username=self.username, group="hotel_admin")
        self.client.login(username=user.username, password=PASSWORD)

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

    def test_register_step2_update_info(self):
        # Dave tries to go back and Edit the Hotel and it takes him to the UpdateView
        hotel = create_hotel()
        user = create_hotel_user(hotel, group="hotel_admin")
        self.client.login(username=user.username, password=PASSWORD)

        response = self.client.get(reverse('main:register_step2'), follow=True)
        self.assertRedirects(response, reverse('main:register_step2_update', kwargs={'pk': hotel.pk}))
        self.assertIsInstance(response.context['form'], HotelCreateForm)

    def test_register_step2_validate_phone_in_use(self):
        other_hotel = create_hotel()
        hotel = create_hotel()
        user = create_hotel_user(hotel, group="hotel_admin")
        self.client.login(username=user.username, password=PASSWORD)
        # try to update to "other_hotel's" ``address_phone``
        CREATE_HOTEL_DICT['address_phone'] = ph_formatter(other_hotel.address_phone)
        response = self.client.post(reverse('main:register_step2_update', kwargs={'pk': hotel.pk}),
            CREATE_HOTEL_DICT)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'address_phone',
            HotelCreateForm.error_messages['duplicate_address_phone'])


class HotelViewTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, group='hotel_admin')

    def tearDown(self):
        self.client.logout()

    def test_update_get(self):
        """
        A "Hotel Admin" can visit their Hotel UpdateView
        """
        self.client.login(username=self.user.username, password=PASSWORD)

        response = self.client.get(reverse('main:hotel_update', kwargs={'pk': self.hotel.pk}))

        self.assertEqual(response.status_code, 200)

    def test_update_get_other_user__mgr_plus(self):
        other_hotel = create_hotel()
        user = create_hotel_user(other_hotel, group='hotel_manager')
        self.client.login(username=user.username, password=PASSWORD)

        response = self.client.get(reverse('main:hotel_update', kwargs={'pk': self.hotel.pk}))

        self.assertEqual(response.status_code, 403)

    def test_update_get_other_user__none_mgr_plus(self):
        other_hotel = create_hotel()
        user = create_hotel_user(other_hotel)
        self.client.login(username=user.username, password=PASSWORD)

        response = self.client.get(reverse('main:hotel_update', kwargs={'pk': self.hotel.pk}))

        self.assertEqual(response.status_code, 403)

    def test_update_get_other_manager(self):
        """
        Managers should not be able to access this View.
        """
        user = create_hotel_user(self.hotel, group='hotel_manager')
        self.client.login(username=user.username, password=PASSWORD)

        response = self.client.get(reverse('main:hotel_update', kwargs={'pk': self.hotel.pk}),
            follow=True)

        self.assertRedirects(
            response,
            reverse('login') + '?next=' + '/account/hotel/update/{}/'.format(self.hotel.pk)
        )


class HotelViewUpdateTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, group='hotel_admin')
        # data
        self.data = {
            'name': self.hotel.name,
            'address_phone': self.hotel.address_phone,
            'address_line1': self.hotel.address_line1,
            'address_city': self.hotel.address_city,
            'address_state': self.hotel.address_state,
            'address_zip': self.hotel.address_zip
        }
        # login
        self.client.login(username=self.user.username, password=PASSWORD)

    def tearDown(self):
        self.client.logout()

    def test_update_post(self):
        """
        Dave changes his street address, and the change is saved in the DB
        """
        self.data['address_phone'] = create._generate_ph()

        response = self.client.post(reverse('main:hotel_update', kwargs={'pk': self.hotel.pk}),
            self.data, follow=True)

        self.assertRedirects(response, reverse('main:user_detail', kwargs={'pk': self.user.pk}))
        updated_hotel = Hotel.objects.get(admin_id=self.user.pk)
        self.assertNotEqual(self.hotel.address_phone, updated_hotel.address_phone)
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
        self.admin = create_hotel_user(hotel=self.hotel, username='admin', group='hotel_admin')
        self.mgr = create_hotel_user(hotel=self.hotel, username='mgr', group='hotel_manager')
        self.user = create_hotel_user(hotel=self.hotel, username='user')

    def test_user_detail(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('main:user_detail', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)

    def test_create(self):
        # both have a hotel attr
        self.assertIsInstance(self.user.profile.hotel, Hotel)
        self.assertIsInstance(self.mgr.profile.hotel, Hotel)

        # mgr is a "hotel_manager"
        mgr_group = Group.objects.get(name="hotel_manager")
        self.assertIn(mgr_group, self.mgr.groups.all())

    def test_update_get(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('main:user_update', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)

    def test_update_post_success(self):
        fname = self.user.first_name

        self.client.login(username=self.user.username, password=self.password)
        response = self.client.post(reverse('main:user_update', kwargs={'pk': self.user.pk}),
            {'first_name': 'new name', 'last_name': self.user.last_name, 'email': self.user.email},
            follow=True)

        self.assertRedirects(response, reverse('main:user_detail', kwargs={'pk': self.user.pk}))
        updated_user = User.objects.get(username=self.user.username)
        self.assertNotEqual(fname, updated_user.first_name)

        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        self.assertEqual(str(m[0]), dj_messages['profile_updated'])

    def test_update_other_users_cant_access(self):
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:user_update', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 403)

    # test ``main.templatetags.user_tags.user_has_group``

    def test_user_has_group__can_view(self):
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('account'))
        self.assertIn('Hotel Info', response.content)
        self.assertIn('Add a Manager', response.content)
        self.assertIn('Auto Replies', response.content)
        self.assertIn('Phone Numbers', response.content)
        self.assertIn('Billing', response.content)

    def test_user_has_group__cannot_view(self):
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('account'))
        self.assertNotIn('Hotel Info', response.content)
        self.assertNotIn('Add a Manager', response.content)
        self.assertNotIn('Auto Replies', response.content)
        self.assertNotIn('Phone Numbers', response.content)
        self.assertNotIn('Billing', response.content)


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

    def test_detail(self):
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:manage_user_detail', kwargs={'pk':self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['breadcrumbs'])
        self.assertTrue(response.context['user_dict'])
        self.assertTrue(response.context['hotel'])
        # can't view "edit" link b/c not admin
        self.assertNotIn(reverse('main:hotel_update', kwargs={'pk': self.hotel.pk}), response.content)

    def test_detail_admin(self):
        # can view "edit" link b/c is an admin
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('main:manage_user_detail', kwargs={'pk':self.user.pk}))
        self.assertIn(reverse('main:hotel_update', kwargs={'pk': self.hotel.pk}), response.content)

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

    def test_create_user_breadcrumbs(self):
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:create_user'))
        self.assertTrue(response.context['breadcrumbs'])

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

    def test_create_mgr_breadcrumbs(self):
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:create_manager'))
        self.assertTrue(response.context['breadcrumbs'])


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

    def test_update_breadcrumbs(self):
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:manage_user_update', kwargs={'pk': self.user.pk}))
        self.assertTrue(response.context['breadcrumbs'])

    def test_delete(self):
        # get
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:manage_user_delete', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user.username, response.context['addit_info'])
        # delete => only hides
        self.assertFalse(self.user.profile.hidden)
        response = self.client.post(reverse('main:manage_user_delete', kwargs={'pk': self.user.pk}), follow=True)
        self.assertRedirects(response, reverse('main:manage_user_list'))
        self.user = User.objects.get(pk=self.user.pk)
        self.assertTrue(self.user.profile.hidden)

    def test_delete_admin(self):
        self.client.login(username=self.mgr.username, password=self.password)

        response = self.client.post(reverse('main:manage_user_delete',
                kwargs={'pk': self.admin.pk}))

        self.assertEqual(response.status_code, 200)
        # error message
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        self.assertEqual(str(m[0]), dj_messages['delete_admin_fail'])

    def test_delete_breadcrumbs(self):
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:manage_user_delete', kwargs={'pk': self.user.pk}))
        self.assertTrue(response.context['breadcrumbs'])
