import os
import time
import pytest
import random
import datetime

from django.db import models
from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.http import Http404
from django.utils import timezone

from model_mommy import mommy

from account.models import (AcctStmt, TransType, AcctTrans, AcctCost,
    CHARGE_AMOUNTS, BALANCE_AMOUNTS)
from account.tests.factory import make_acct_stmts, make_acct_trans
from main.models import Hotel
from main.tests.factory import (create_hotel, make_subaccount,
    CREATE_USER_DICT, CREATE_HOTEL_DICT)
from payment.models import Customer
from utils import create


class RegistrationTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.username = CREATE_USER_DICT['username']
        self.password = '1234'

    def test_register_step3(self):
        # Step 1
        response = self.client.post(reverse('main:register_step1'),
            CREATE_USER_DICT)
        self.client.login(username=self.username, password=self.password)
        # Step 2
        response = self.client.post(reverse('main:register_step2'),
            CREATE_HOTEL_DICT)

        # Step 3
        response = self.client.post(reverse('register_step3'),
            {'init_amt': CHARGE_AMOUNTS[0][0],
            'balance_min': BALANCE_AMOUNTS[0][0],
            'recharge_amt': CHARGE_AMOUNTS[0][0]}, follow=True)
        self.assertRedirects(response, reverse('payment:register_step4'))
        # created n linked to Hotel
        acct_cost = AcctCost.objects.all()
        assert len(acct_cost) == 1
        assert acct_cost[0].hotel == Hotel.objects.get(name=CREATE_HOTEL_DICT['name'])


class RenderTests(TestCase):
    # Test Rending of view, template path is correct, url
    # User of each permission type needed

    def setUp(self):
        create._get_groups_and_perms()
        self.password = '1234'

        # Admin
        self.admin = User.objects.create_user('admin', settings.DEFAULT_FROM_EMAIL, self.password)
        self.admin_group = Group.objects.get(name="hotel_admin")
        self.admin.groups.add(self.admin_group)
        self.admin.save()

        # Manager
        self.manager = User.objects.create_user('manager', settings.DEFAULT_FROM_EMAIL, self.password)
        self.manager_group = Group.objects.get(name="hotel_manager")
        self.manager.groups.add(self.manager_group)
        self.manager.save()

        # User
        self.user = User.objects.create_user('user', settings.DEFAULT_FROM_EMAIL, self.password)


    ### inherit from - django.contrib.auth.forms

    def test_login(self):
        response = self.client.get(reverse('login'))
        assert response.status_code == 200
        assert response.context['form']

    ### 2 views for password change

    def test_password_change(self):
        # login required view
        response = self.client.get(reverse('password_change'))
        assert response.status_code == 302

        # login
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('password_change'))
        assert response.status_code == 200
        assert response.context['form']

    def test_password_change_done(self):
        # login required view
        response = self.client.get(reverse('password_change_done'))
        assert response.status_code == 302

        # login
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('password_change_done'))
        assert response.status_code == 200

    ### 4 views for password reset

    def test_password_reset(self):
        response = self.client.get(reverse('password_reset'))
        assert response.status_code == 200
        assert response.context['form']

    def test_password_reset_done(self):
        response = self.client.get(reverse('password_reset_done'))
        assert response.status_code == 200

    def test_password_reset_confirm(self):
        # TODO: write an integration for Form test for this
        pass

    def test_password_reset_complete(self):
        response = self.client.get(reverse('password_reset_complete'))
        assert response.status_code == 200


class LoginTests(TestCase):

    def setUp(self):
        self.password = '1111'
        self.user = User.objects.create_user('Bobby',
            settings.DEFAULT_FROM_EMAIL, self.password)

    def test_get(self):
        response = self.client.get(reverse('login'))
        assert response.status_code == 200
        assert response.context['form']  


class PasswordChangeTests(TestCase):

    def setUp(self):
        self.password = '1111'
        self.new_password = '2222'
        self.user = User.objects.create_user('Bobby',
            settings.DEFAULT_FROM_EMAIL, self.password)

    def test_get(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('password_change'))
        assert response.status_code == 200
        assert response.context['form']

    def test_get_done(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('password_change_done'))
        assert response.status_code == 200


class PasswordResetTests(TestCase):

    def setUp(self):
        self.password = '1111'
        self.new_password = '2222'
        self.user = User.objects.create_user('Bobby',
            settings.DEFAULT_FROM_EMAIL, self.password)

    def test_get(self):
        response = self.client.get(reverse('password_reset'))
        assert response.status_code == 200
        assert response.context['form']

    def test_get_done(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('password_reset_done'))
        assert response.status_code == 200

    def test_get_done(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('password_reset_complete'))
        assert response.status_code == 200


class RoutingViewTests(TestCase):

    def setUp(self):
        self.password = '1111'
        self.user = User.objects.create_user('Bobby',
            settings.DEFAULT_FROM_EMAIL, self.password)

    def test_private(self):
        # Not logged in get()
        response = self.client.get(reverse('private'))
        assert response.status_code == 302

        # Logged in
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('private'), follow=True)
        self.assertRedirects(response, reverse('account'))

    def test_login_error(self):
        response = self.client.get(reverse('login_error'), follow=True)
        self.assertRedirects(response, reverse('login'))

    def test_logout(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('logout'), follow=True)
        self.assertRedirects(response, reverse('login'))

    def test_verify_logout(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('verify_logout'))
        assert response.status_code == 200


# class AcctStmtViewTests(TestCase):

#     def setUp(self):
#         self.password = '1234'
#         self.hotel = create_hotel()
#         self.other_hotel = create_hotel('other')

#         # create "Hotel Manager" Group
#         create._get_groups_and_perms()

#         # Admin
#         self.admin = mommy.make(User, username='admin')
#         self.admin.groups.add(Group.objects.get(name="hotel_admin"))
#         self.admin.set_password(self.password)
#         self.admin.save()
#         self.admin.profile.update_hotel(hotel=self.hotel)
#         # Hotel Admin ID
#         self.hotel.admin_id = self.admin.id
#         self.hotel.save()

#         # Manager
#         self.mgr = mommy.make(User, username='mgr')
#         self.mgr.groups.add(Group.objects.get(name="hotel_manager"))
#         self.mgr.set_password(self.password)
#         self.mgr.save()
#         self.mgr.profile.update_hotel(hotel=self.hotel)

#         # User
#         self.user = mommy.make(User, username='user')
#         self.user.set_password(self.password)
#         self.user.save()
#         self.user.profile.update_hotel(hotel=self.hotel)

#         # Other Hotel Admin
#         self.other_admin = mommy.make(User, username='other_admin')
#         self.other_admin.groups.add(Group.objects.get(name="hotel_admin"))
#         self.other_admin.set_password(self.password)
#         self.other_admin.save()
#         self.other_admin.profile.update_hotel(hotel=self.other_hotel)

#         make_acct_stmts(hotel=self.hotel)

#     def test_create(self):
#         assert AcctStmt.objects.all()
#         assert AcctStmt.objects.filter(hotel=self.hotel)

#     def test_AdminOnlyMixin(self):
#         assert self.admin.profile.hotel == self.hotel
#         assert self.admin.id == self.hotel.admin_id
#         assert Group.objects.get(name="hotel_admin") in self.admin.groups.all()

#     def test_list(self):
#         # Admin can access, and acct stmts in list
#         response = self.client.get(reverse('login'))
#         assert response.status_code == 200

#         # Admin has full access
#         self.client.login(username=self.admin.username, password=self.password)
#         response = self.client.get(reverse('login'))
#         assert response.status_code == 302

#         response = self.client.get(reverse('acct_stmt_list'))
#         assert response.status_code == 200

#         # User can't access
#         self.client.logout()
#         self.client.login(username=self.user.username, password=self.password)
#         response = self.client.get(reverse('acct_stmt_list'))
#         print(response.status_code)
#         assert response.status_code == 404

#         # Mgr can't access
#         self.client.logout()
#         self.client.login(username=self.mgr.username, password=self.password)
#         response = self.client.get(reverse('acct_stmt_list'))
#         assert response.status_code == 404

#         # Other Admin get's 404 can't access
#         self.client.logout()
#         self.client.login(username=self.other_admin.username, password=self.password)
#         response = self.client.get(reverse('acct_stmt_list'))
#         assert response.status_code == 404

#     def test_detail(self):
#         # Admin has full access
#         self.client.login(username=self.admin.username, password=self.password)
#         acct_stmt = AcctStmt.objects.first()
#         response = self.client.get(reverse('acct_stmt_detail', kwargs={'pk': acct_stmt.pk}))
#         assert response.status_code == 200


# class AcctTransViewTests(TestCase):

#     fixtures = ['account.json']

#     def setUp(self):
#         self.password = '1234'
#         self.hotel = create_hotel()
#         self.other_hotel = create_hotel('other')

#         # create "Hotel Manager" Group
#         create._get_groups_and_perms()

#         # Admin
#         self.admin = mommy.make(User, username='admin')
#         self.admin.groups.add(Group.objects.get(name="hotel_admin"))
#         self.admin.set_password(self.password)
#         self.admin.save()
#         self.admin.profile.update_hotel(hotel=self.hotel)
#         # Hotel Admin ID
#         self.hotel.admin_id = self.admin.id
#         self.hotel.save()

#         # Manager
#         self.mgr = mommy.make(User, username='mgr')
#         self.mgr.groups.add(Group.objects.get(name="hotel_manager"))
#         self.mgr.set_password(self.password)
#         self.mgr.save()
#         self.mgr.profile.update_hotel(hotel=self.hotel)

#         # User
#         self.user = mommy.make(User, username='user')
#         self.user.set_password(self.password)
#         self.user.save()
#         self.user.profile.update_hotel(hotel=self.hotel)

#         # Other Hotel Admin
#         self.other_admin = mommy.make(User, username='other_admin')
#         self.other_admin.groups.add(Group.objects.get(name="hotel_admin"))
#         self.other_admin.set_password(self.password)
#         self.other_admin.save()
#         self.other_admin.profile.update_hotel(hotel=self.other_hotel)

#         self.acct_stmts = make_acct_stmts(hotel=self.hotel)

#         self.acct_trans = make_acct_trans(hotel=self.hotel)

#     def test_create(self):
#         # All acct_trans are created
#         assert self.acct_trans

#         balance = AcctTrans.objects.all_trans(hotel=self.hotel).balance()
#         assert balance > 0

#     def test_list(self):
#         self.client.login(username=self.admin.username, password=self.password)
#         response = self.client.get(reverse('acct_trans_list_view'))
#         assert response.status_code == 200
#         assert response.context['acct_stmts']

#     def test_detail(self):
#         self.client.login(username=self.admin.username, password=self.password)
#         response = self.client.get(reverse('acct_trans_detail_view',
#             kwargs={'year': self.hotel.created.year, 'month': self.hotel.created.month}))
#         assert response.status_code == 200
#         # assert response.context['init_balance']
#         assert response.context['monthly_trans']
#         assert response.context['balance']


# class AccountViewTests(TestCase):

#     def setUp(self):
#         self.password = '1234'
#         self.hotel = create_hotel()

#         # create "Hotel Manager" Group
#         create._get_groups_and_perms()

#         # Admin
#         self.admin = mommy.make(User, username='admin')
#         self.admin.groups.add(Group.objects.get(name="hotel_admin"))
#         self.admin.set_password(self.password)
#         self.admin.save()
#         self.admin.profile.update_hotel(hotel=self.hotel)
#         # Hotel Admin ID
#         self.hotel.admin_id = self.admin.id
#         self.hotel.save()

#         # Manager
#         self.mgr = mommy.make(User, username='mgr')
#         self.mgr.groups.add(Group.objects.get(name="hotel_manager"))
#         self.mgr.set_password(self.password)
#         self.mgr.save()
#         self.mgr.profile.update_hotel(hotel=self.hotel)

#         # User
#         self.user = mommy.make(User, username='user')
#         self.user.set_password(self.password)
#         self.user.save()
#         self.user.profile.update_hotel(hotel=self.hotel)

#         # AccountView needed context objects
#         self.phone_number = make_phone_number(hotel=self.hotel)
#         self.subaccount = make_subaccount(hotel=self.hotel)

#     def test_get(self):
#         self.client.login(username=self.admin.username, password=self.password)
#         response = self.client.get(reverse('account'))
#         assert response.status_code == 200
#         assert response.context['phone_number'] == self.phone_number
#         assert response.context['subaccount'] == self.subaccount
#         assert response.context['hotel'] == self.hotel


# class CloseAcctViewsTests(TestCase):

#     fixtures = ['account.json']

#     def setUp(self):
#         self.password = '1234'
#         self.hotel = create_hotel()
#         self.other_hotel = create_hotel('other')

#         # create "Hotel Manager" Group
#         create._get_groups_and_perms()

#         # Admin
#         self.admin = mommy.make(User, username='admin')
#         self.admin.groups.add(Group.objects.get(name="hotel_admin"))
#         self.admin.set_password(self.password)
#         self.admin.save()
#         self.admin.profile.update_hotel(hotel=self.hotel)
#         # Hotel Admin ID
#         self.hotel.admin_id = self.admin.id
#         self.hotel.save()

#         # Manager
#         self.mgr = mommy.make(User, username='mgr')
#         self.mgr.groups.add(Group.objects.get(name="hotel_manager"))
#         self.mgr.set_password(self.password)
#         self.mgr.save()
#         self.mgr.profile.update_hotel(hotel=self.hotel)

#         # User
#         self.user = mommy.make(User, username='user')
#         self.user.set_password(self.password)
#         self.user.save()
#         self.user.profile.update_hotel(hotel=self.hotel)

#         # Other Hotel Admin
#         self.other_admin = mommy.make(User, username='other_admin')
#         self.other_admin.groups.add(Group.objects.get(name="hotel_admin"))
#         self.other_admin.set_password(self.password)
#         self.other_admin.save()
#         self.other_admin.profile.update_hotel(hotel=self.other_hotel)

#         self.acct_stmts = make_acct_stmts(hotel=self.hotel)

#         self.acct_trans = make_acct_trans(hotel=self.hotel)

#         # Customer
#         self.customer = mommy.make(Customer)
#         self.hotel.customer = self.customer
#         self.hotel.save()

#     def test_close_acct(self):
#         self.client.login(username=self.admin.username, password=self.password)

#         # GET
#         response = self.client.get(reverse('close_acct'))
#         assert response.status_code == 200
#         assert response.context['headline']

#         # POST
#         response = self.client.post(reverse('close_acct'), {}, follow=True)
#         self.assertRedirects(response, reverse('close_acct_confirm',
#             kwargs={'slug': self.hotel.customer.short_pk}))

#     def test_close_acct_confirm(self):
#         self.client.login(username=self.admin.username, password=self.password)

#         # GET
#         response = self.client.get(reverse('close_acct_confirm',
#             kwargs={'slug': self.hotel.customer.short_pk}))
#         assert response.status_code == 200
#         assert response.context['headline']

#         # POST
#         response = self.client.post(reverse('close_acct_confirm',
#             kwargs={'slug': self.hotel.customer.short_pk}), {}, follow=True)
#         self.assertRedirects(response, reverse('close_acct_success'))

#     def test_close_acct_success(self):
#         self.client.login(username=self.admin.username, password=self.password)

#         # GET
#         response = self.client.get(reverse('close_acct_success'))
#         assert response.status_code == 200
#         assert response.context['headline']
#         assert response.context['message']
