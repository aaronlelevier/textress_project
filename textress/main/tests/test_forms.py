import os
import pytest

from django.db import models
from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

import stripe
from model_mommy import mommy

from main.forms import UserCreateForm, HotelCreateForm, UserUpdateForm
from main.models import Hotel, UserProfile, Subaccount
from main.tests.factory import (CREATE_USER_DICT, CREATE_HOTEL_DICT,
    create_hotel, create_hotel_user)
from sms.models import PhoneNumber
from utils import create
from utils.data import STATES, HOTEL_TYPES

stripe.api_key = settings.STRIPE_SECRET_KEY


class RegistrationTests(TestCase):

    # fixtures = ['main.json', 'payment.json']

    def setUp(self):
        create._get_groups_and_perms()

        # Login Credentials
        self.username = 'test'
        self.password = '1234'

    def test_register_step1(self):
        # 1st step to register Admin User, so the Dave see's the normal form
        response = self.client.get(reverse('main:register_step1'))
        assert isinstance(response.context['form'], UserCreateForm)

        # Dave submits info successfully
        response = self.client.post(reverse('main:register_step1'),
            CREATE_USER_DICT, follow=True)
        self.assertRedirects(response, reverse('main:register_step2'))
        user = User.objects.get(username=CREATE_USER_DICT['username'])
        assert isinstance(user, User)
        assert isinstance(user.profile, UserProfile)
        assert user == User.objects.get(groups__name='hotel_admin')

        # Dave wants to go back and update his email, so he now get's the Update Form
        response = self.client.get(reverse('main:register_step1_update', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, 200)
        assert isinstance(response.context['form'], UserUpdateForm)

        # Dave logs out and now can't access the RegisterAdminUpdateView
        self.client.logout()
        response = self.client.get(reverse('main:register_step1_update', kwargs={'pk': user.pk}))
        self.assertNotEqual(response.status_code, 200)

    def test_register_step2(self):
        # Step 1
        response = self.client.post(reverse('main:register_step1'),
            CREATE_USER_DICT)
        self.client.login(username=self.username, password=self.password)

        # Step 2
        # Dave goes to register his Hotel's info
        response = self.client.get(reverse('main:register_step2'))
        assert isinstance(response.context['form'], HotelCreateForm)
        # Dave submits his info
        response = self.client.post(reverse('main:register_step2'),
            CREATE_HOTEL_DICT)
        # Now he goes back to make a change
        user = User.objects.get(username=CREATE_USER_DICT['username'])
        hotel = user.profile.hotel
        response = self.client.get(reverse('main:register_step2_update', kwargs={'pk': hotel.pk}))
        self.assertEqual(response.status_code, 200)
        assert isinstance(response.context['form'], HotelCreateForm)

        # Logged out Dave can't access either View
        self.client.logout()
        # step 2
        response = self.client.get(reverse('main:register_step2'))
        self.assertNotEqual(response.status_code, 200)
        # step 2 update
        response = self.client.get(reverse('main:register_step2_update', kwargs={'pk': hotel.pk}))
        self.assertNotEqual(response.status_code, 200)


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

    def test_detail(self):
        # User Can Login
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('main:user_update', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 200)
        assert response.context['object'] == self.user

        # Mgr can't access
        self.client.logout()
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:user_update', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 403)

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


class ManageUsersTests(TestCase):

    def setUp(self):
        self.password = '1234'
        self.hotel = create_hotel()

        # create "Hotel Manager" Group
        create._get_groups_and_perms()

        # Users
        self.mgr = create_hotel_user(hotel=self.hotel, username='mgr', group='hotel_manager')
        self.user = create_hotel_user(hotel=self.hotel, username='user')

    def test_list(self):
        # mgr can access
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:manage_user_list'))
        assert response.status_code == 200

        # normal user cannot
        self.client.logout()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('main:manage_user_list'))
        assert response.status_code == 302


    ### CREATE USER ###

    def test_create_user_get(self):
        # mgr can access
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:create_user'))
        assert response.status_code == 200

        # normal user cannot
        self.client.logout()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('main:create_user'))
        assert response.status_code == 302

    def test_create_user_post(self):
        # mgr can access
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.post(reverse('main:create_user'),
            {'first_name': 'fname', 'last_name': 'lname',
            'email': settings.DEFAULT_TO_EMAIL, 'username': 'test_create',
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
        assert response.status_code == 200

        # normal user cannot
        self.client.logout()
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('main:create_manager'))
        assert response.status_code == 302

    def test_create_mgr_post(self):
        # mgr can access
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.post(reverse('main:create_manager'),
            {'first_name': 'fname', 'last_name': 'lname',
            'email': settings.DEFAULT_TO_EMAIL, 'username': 'test_create_mgr',
            'password1': self.password, 'password2': self.password},
            follow=True)

        # new MGR created, is part of Mgr Group, redirects to "Manage Users List"
        new_user = User.objects.get(username='test_create_mgr')
        assert isinstance(new_user, User)
        assert Group.objects.get(name="hotel_manager") in new_user.groups.all()
        self.assertRedirects(response, reverse('main:manage_user_list'))

    def test_update(self):
        # User can update
        fname = self.user.first_name

        # User can't Access
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('main:manage_user_update', kwargs={'pk': self.user.pk}))
        assert response.status_code == 302

        # Mgr Only can Access
        self.client.logout()
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('main:manage_user_update', kwargs={'pk': self.user.pk}))
        assert response.status_code == 200

        # Post
        response = self.client.post(reverse('main:manage_user_update', kwargs={'pk': self.user.pk}),
            {'first_name': 'mgr new name', 'last_name': self.user.last_name, 'email': self.user.email},
            follow=True)
        # User updated n redirects
        updated_user = User.objects.get(username=self.user.username)
        assert fname != updated_user.first_name
        self.assertRedirects(response, reverse('main:manage_user_list'))
