import os
import time
import pytest
import stripe

from django.conf import settings
from django.test import TestCase, LiveServerTestCase, RequestFactory
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group
from django.http import Http404

from model_mommy import mommy

from account.models import AcctCost, AcctStmt, AcctTrans, CHARGE_AMOUNTS, BALANCE_AMOUNTS
from account.tests.factory import (CREATE_ACCTCOST_DICT, create_acct_stmts,
    create_acct_trans)
from main.models import Hotel
from main.tests.factory import (CREATE_USER_DICT, CREATE_HOTEL_DICT, PASSWORD,
    create_hotel, create_hotel_user)
from payment.tests import factory
from payment.models import Customer, Card, Charge
from sms.models import PhoneNumber
from utils import create
from utils.email import Email


class RegistrationTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.username = CREATE_USER_DICT['username']
        self.password = '1234'

        # Step 1
        response = self.client.post(reverse('main:register_step1'),
            CREATE_USER_DICT)
        self.client.login(username=self.username, password=self.password)
        # Step 2
        response = self.client.post(reverse('main:register_step2'),
            CREATE_HOTEL_DICT)
        # Step 3
        response = self.client.post(reverse('register_step3'), # no namespace b/c in "account" app
            CREATE_ACCTCOST_DICT)

    def test_register_step4_get(self):
        # Step 4
        response = self.client.get(reverse('payment:register_step4'))
        self.assertEqual(response.status_code, 200)
        
    def test_register_step4_context(self):
        # Step 4
        response = self.client.get(reverse('payment:register_step4'))
        assert isinstance(response.context['acct_cost'], AcctCost)
        assert response.context['months']
        assert response.context['years']
        assert response.context['PHONE_NUMBER_CHARGE']

        self.assertContains(response, response.context['step'])
        self.assertContains(response, response.context['step_number'])

    def test_register_success(self):
        # valid Customer, so can access
        customer = mommy.make(Customer)
        hotel = Hotel.objects.first()
        hotel = hotel.update_customer(customer)
        response = self.client.get(reverse('payment:register_success'))
        self.assertEqual(response.status_code, 200)

    def test_register_success_fail(self):
        # random Admin User who hasn't paid gets redirected
        # Users
        hotel_b = create_hotel(name='hotel_b')
        admin_b = create_hotel_user(hotel=hotel_b, username='admin_b', group='hotel_admin')
        hotel_b = hotel_b.set_admin_id(user=admin_b)

        self.client.login(username=admin_b.username, password=self.password)
        response = self.client.get(reverse('payment:register_success'))
        self.assertRedirects(response, reverse('payment:register_step4'))


class PaymentEmailTests(TestCase):
    
    def setUp(self):
        create._get_groups_and_perms()
        self.username = CREATE_USER_DICT['username']
        self.password = PASSWORD

        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel)
        self.client.login(username=self.username, password=self.password)

    def test_email(self):
        user = User.objects.first()
        customer = mommy.make(Customer, email=user.email)
        charge = mommy.make(Charge, customer=customer)

        email = Email(
            to=user.email,
            from_email=settings.DEFAULT_EMAIL_BILLING,
            extra_context={
                'user': user,
                'customer': customer,
                'charge': charge
            },
            subject='email/payment_subject.txt',
            html_content='email/payment_email.html'
        )
        email.msg.send()


class BillingTests(TestCase):

    def setUp(self):
        self.password = PASSWORD
        self.hotel = create_hotel()

        # create "Hotel Manager" Group
        create._get_groups_and_perms()

        # Users
        self.admin = create_hotel_user(hotel=self.hotel, username='admin', group='hotel_admin')
        self.user = create_hotel_user(hotel=self.hotel, username='user')

        self.client.login(username=self.admin.username, password=PASSWORD)

        # Billing Stmt Fixtures
        self.acct_cost, created = AcctCost.objects.get_or_create(self.hotel)
        self.acct_stmts = create_acct_stmts(self.hotel)
        self.acct_trans = create_acct_trans(self.hotel)
        self.phone_number = mommy.make(PhoneNumber, hotel=self.hotel)

    def tearDown(self):
        self.client.logout()

    ### BillingSummaryView ###

    def test_summmary_get(self):
        response = self.client.get(reverse('payment:summary'))
        self.assertEqual(response.status_code, 200)

    def test_summary_context(self):
        response = self.client.get(reverse('payment:summary'))
        self.assertIsInstance(response.context['acct_stmt'], AcctStmt)
        # User's current fund's balance show's in context
        self.assertIsNotNone(response.context['acct_stmts'][0].balance)
        # Other context
        self.assertIsInstance(response.context['acct_trans'][0], AcctTrans)
        self.assertIsInstance(response.context['acct_cost'], AcctCost)
        self.assertIsInstance(response.context['phone_numbers'][0], PhoneNumber)

