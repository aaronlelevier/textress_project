import os
import pytest
from unittest.mock import MagicMock

from django.db import models
from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

from model_mommy import mommy

from ..models import Hotel, UserProfile, Subaccount
from sms.models import PhoneNumber
from utils import create
from utils.data import STATES, HOTEL_TYPES

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

from .factory import create_hotel


def create_admin():
    "`hotel_admin` Group Obj needs to be pre created for this to work."
    admin = User.objects.create(username="Admin", email="pyaaron@gmail.com",
        password="1234", is_superuser=True, is_staff=True)
    admin_group = Group.objects.get(name="hotel_admin")
    admin.groups.add(admin_group)
    admin.set_password("1234")
    admin.save()
    return admin


class BasicTests(TestCase):

    def setUp(self):
        self.username = 'test'
        self.password = '1234'
        self.email = settings.DEFAULT_TO_EMAIL

    def test_create_user(self):
        user = User.objects.create(username=self.username,
                                   email=self.email,
                                   password=self.password)
        assert isinstance(user, User)        


class RenderTests(TestCase):

    def test_index_get(self):
        response = self.client.get(reverse('main:index'))
        assert response.status_code == 200

    def test_terms(self):
        response = self.client.get(reverse('main:terms_n_cond'))
        assert response.status_code == 200
        assert response.context['company']
        assert response.context['LLC']


class RegistrationTests(TestCase):

    fixtures = ['main.json', 'payment.json']

    def setUp(self):
        self.factory = RequestFactory()
        create._get_groups_and_perms()

    ### SUCCESSFUL REGISTRATION TESTs ###

    def test_register_step1(self):
        response = self.client.post(reverse('main:register_step1'),
            {'username':'test', 'first_name': 'Test', 'last_name': 'Test',
            'email':settings.DEFAULT_TO_EMAIL,
            'password1':'1234', 'password2':'1234'},
            follow=True)

        self.assertRedirects(response, reverse('main:register_step2'))

        user = User.objects.get(username='test')
        assert isinstance(user, User)
        assert isinstance(user.profile, UserProfile)
        assert user == User.objects.get(groups__name='hotel_admin')

#     def test_register_step2(self):
#         # Step 1
#         response = self.client.post(reverse('main:register_step1'),
#             {'username':'test', 'first_name': 'Test', 'last_name': 'Test',
#             'email':settings.DEFAULT_TO_EMAIL,
#             'password1':'1234', 'password2':'1234'})

#         # Tests
#         response = self.client.get(reverse('main:register_step2'))
#         assert response.status_code == 200

#         response = self.client.post(reverse('main:register_step2'),
#             {'name': 'Test Hotel',
#             'phone': '6195105555',
#             'address_line1': '123 Some St.',
#             'address_city': 'San Diego',
#             'address_state': STATES[0][0],
#             'address_zip': '92131'}, follow=True)

#         self.assertRedirects(response, reverse('payment:register_step3'))

#         hotel = Hotel.objects.get(name='Test Hotel')
#         updated_user = User.objects.get(username='test')
#         assert hotel.admin_id == updated_user.id
#         assert updated_user.profile.hotel == hotel

#     def test_register_step3(self):
#         # Plan choice
#         plan = Plan.objects.get(name="Bronze")
#         assert isinstance(plan, Plan)

#         # Step 1
#         response = self.client.post(reverse('main:register_step1'),
#             {'username':'test', 'first_name': 'Test', 'last_name': 'Test',
#             'email':settings.DEFAULT_TO_EMAIL,
#             'password1':'1234', 'password2':'1234'})
#         # Step 2
#         response = self.client.post(reverse('main:register_step2'),
#             {'name': 'Test Hotel',
#             'phone': '6195105555',
#             'address_line1': '123 Some St.',
#             'address_city': 'San Diego',
#             'address_state': STATES[0][0],
#             'address_zip': '92131'}, follow=True)

#         # Step 3
#         response = self.client.post(reverse('payment:register_step3'),
#             {'plan': 'Bronze'}, follow=True)
#         # TODO: This needs a Plan.save() monkey-patch, so it doesn't create a 
#         #   Twilio Plan each time. Also, tries to save the choice in `request.session`
#         #   which I need to figure out how to use in Testing
#         # self.assertRedirects(response, reverse('payment:register_step4'))


#     ### FAILING TESTS ###

#     def test_register_step2_loggedOut(self):
#         response = self.client.get(reverse('main:register_step2'), follow=True)
#         self.assertRedirects(response, '/accounts/login/?next=/register/step2/')


# class UserViewTests(TestCase):

#     def setUp(self):
#         self.password = '1234'
#         self.hotel = create_hotel()

#         # create "Hotel Manager" Group
#         create._get_groups_and_perms()

#         # Manager
#         self.mgr = mommy.make(User, username='mgr')
#         self.mgr.groups.add(Group.objects.get(name="hotel_manager"))
#         self.mgr.set_password(self.password)
#         self.mgr.save()
#         self.mgr.profile.update_hotel(hotel=self.hotel)

#         self.user = mommy.make(User, username='user')
#         self.user.set_password(self.password)
#         self.user.save()
#         self.user.profile.update_hotel(hotel=self.hotel)

#     def test_create(self):
#         # both have a hotel attr
#         assert isinstance(self.user.profile.hotel, Hotel)
#         assert isinstance(self.mgr.profile.hotel, Hotel)

#         # mgr is a "hotel_manager"
#         mgr_group = Group.objects.get(name="hotel_manager")
#         assert mgr_group in self.mgr.groups.all()

#     def test_detail(self):
#         # User Can Login
#         self.client.login(username=self.user.username, password=self.password)
#         response = self.client.get(reverse('main:user_detail', kwargs={'pk': self.user.pk}))
#         assert response.status_code == 200
#         assert response.context['object'] == self.user

#         # Mgr can't access
#         self.client.logout()
#         self.client.login(username=self.mgr.username, password=self.password)
#         response = self.client.get(reverse('main:user_detail', kwargs={'pk': self.user.pk}))
#         assert response.status_code == 404

#     def test_update(self):
#         # User can update
#         fname = self.user.first_name

#         # Mgr can't Access
#         self.client.login(username=self.mgr.username, password=self.password)
#         response = self.client.get(reverse('main:user_update', kwargs={'pk': self.user.pk}))
#         assert response.status_code == 404

#         # Login n Get
#         self.client.logout()
#         self.client.login(username=self.user.username, password=self.password)
#         response = self.client.get(reverse('main:user_update', kwargs={'pk': self.user.pk}))
#         assert response.status_code == 200

#         # Post
#         response = self.client.post(reverse('main:user_update', kwargs={'pk': self.user.pk}),
#             {'first_name': 'new name', 'last_name': self.user.last_name, 'email': self.user.email},
#             follow=True)
#         # User updated n redirects
#         updated_user = User.objects.get(username=self.user.username)
#         assert fname != updated_user.first_name
#         self.assertRedirects(response, reverse('main:user_detail',
#             kwargs={'pk': updated_user.pk}))



# class ManageUsersTests(TestCase):

#     def setUp(self):
#         self.password = '1234'
#         self.hotel = create_hotel()

#         # create "Hotel Manager" Group
#         create._get_groups_and_perms()

#         # Manager
#         self.mgr = mommy.make(User, username='mgr')
#         self.mgr.groups.add(Group.objects.get(name="hotel_manager"))
#         self.mgr.set_password(self.password)
#         self.mgr.save()
#         self.mgr.profile.update_hotel(hotel=self.hotel)

#         self.user = mommy.make(User, username='user')
#         self.user.set_password(self.password)
#         self.user.save()
#         self.user.profile.update_hotel(hotel=self.hotel)

#     def test_list(self):
#         # mgr can access
#         self.client.login(username=self.mgr.username, password=self.password)
#         response = self.client.get(reverse('main:manage_user_list'))
#         assert response.status_code == 200

#         # normal user cannot
#         self.client.logout()
#         self.client.login(username=self.user.username, password=self.password)
#         response = self.client.get(reverse('main:manage_user_list'))
#         assert response.status_code == 302

#     def test_detail(self):
#         # mgr can access
#         self.client.login(username=self.mgr.username, password=self.password)
#         response = self.client.get(reverse('main:manage_user_detail',
#             kwargs={'pk': self.user.pk}))
#         assert response.status_code == 200

#         # normal user cannot
#         self.client.logout()
#         self.client.login(username=self.user.username, password=self.password)
#         response = self.client.get(reverse('main:manage_user_detail',
#             kwargs={'pk': self.user.pk}))
#         assert response.status_code == 302


#     ### CREATE USER ###

#     def test_create_user_get(self):
#         # mgr can access
#         self.client.login(username=self.mgr.username, password=self.password)
#         response = self.client.get(reverse('main:create_user'))
#         assert response.status_code == 200

#         # normal user cannot
#         self.client.logout()
#         self.client.login(username=self.user.username, password=self.password)
#         response = self.client.get(reverse('main:create_user'))
#         assert response.status_code == 302

#     def test_create_user_post(self):
#         # mgr can access
#         self.client.login(username=self.mgr.username, password=self.password)
#         response = self.client.post(reverse('main:create_user'),
#             {'first_name': 'fname', 'last_name': 'lname',
#             'email': settings.DEFAULT_TO_EMAIL, 'username': 'test_create',
#             'password1': self.password, 'password2': self.password},
#             follow=True)

#         # new User created, redirects to "Manage Users List"
#         new_user = User.objects.get(username='test_create')
#         assert isinstance(new_user, User)
#         self.assertRedirects(response, reverse('main:manage_user_list'))


#     ### CREATE MGR ###

#     def test_create_mgr_get(self):
#         # mgr can access
#         self.client.login(username=self.mgr.username, password=self.password)
#         response = self.client.get(reverse('main:create_manager'))
#         assert response.status_code == 200

#         # normal user cannot
#         self.client.logout()
#         self.client.login(username=self.user.username, password=self.password)
#         response = self.client.get(reverse('main:create_manager'))
#         assert response.status_code == 302

#     def test_create_mgr_post(self):
#         # mgr can access
#         self.client.login(username=self.mgr.username, password=self.password)
#         response = self.client.post(reverse('main:create_manager'),
#             {'first_name': 'fname', 'last_name': 'lname',
#             'email': settings.DEFAULT_TO_EMAIL, 'username': 'test_create_mgr',
#             'password1': self.password, 'password2': self.password},
#             follow=True)

#         # new MGR created, is part of Mgr Group, redirects to "Manage Users List"
#         new_user = User.objects.get(username='test_create_mgr')
#         assert isinstance(new_user, User)
#         assert Group.objects.get(name="hotel_manager") in new_user.groups.all()
#         self.assertRedirects(response, reverse('main:manage_user_list'))


#     # NEXT: Add tests for "Update" from Mgr point of view

#     def test_update(self):
#         # User can update
#         fname = self.user.first_name

#         # User can't Access
#         self.client.login(username=self.user.username, password=self.password)
#         response = self.client.get(reverse('main:manage_user_update', kwargs={'pk': self.user.pk}))
#         assert response.status_code == 302

#         # Mgr Only can Access
#         self.client.logout()
#         self.client.login(username=self.mgr.username, password=self.password)
#         response = self.client.get(reverse('main:manage_user_update', kwargs={'pk': self.user.pk}))
#         assert response.status_code == 200

#         # Post
#         response = self.client.post(reverse('main:manage_user_update', kwargs={'pk': self.user.pk}),
#             {'first_name': 'mgr new name', 'last_name': self.user.last_name, 'email': self.user.email},
#             follow=True)
#         # User updated n redirects
#         updated_user = User.objects.get(username=self.user.username)
#         assert fname != updated_user.first_name
#         self.assertRedirects(response, reverse('main:manage_user_detail',
#             kwargs={'pk': updated_user.pk}))

#     def test_delete(self):
#         # User to test deleting
#         del_user = User.objects.create(username='del_user', email=settings.DEFAULT_TO_EMAIL,
#             password=self.password)
#         del_user.profile.update_hotel(self.hotel)
#         assert isinstance(del_user, User)
#         assert del_user.profile.hotel == self.hotel

#         # User can't access
#         self.client.login(username=self.user.username, password=self.password)
#         response = self.client.get(reverse('main:manage_user_delete', kwargs={'pk': del_user.pk}))
#         assert response.status_code == 302

#         # Mgr Only can Access
#         self.client.logout()
#         self.client.login(username=self.mgr.username, password=self.password)
#         response = self.client.get(reverse('main:manage_user_delete', kwargs={'pk': del_user.pk}))
#         assert response.status_code == 200

#         # Post
#         response = self.client.post(reverse('main:manage_user_delete', kwargs={'pk': del_user.pk}),
#             follow=True)
#         # User updated n redirects
#         self.assertRedirects(response, reverse('main:manage_user_list'))
#         with pytest.raises(ObjectDoesNotExist):
#             updated_del_user = User.objects.get(username=del_user.username)






