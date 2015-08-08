import os
import time
import pytest
import stripe

from django.conf import settings
from django.test import TestCase, RequestFactory
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
# from payment.forms import StripeOneTimePaymentForm
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
        customer = factory.customer()
        charge = factory.charge(customer.id)

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

    def test_get_summmary(self):
        response = self.client.get(reverse('payment:summary'))
        self.assertEqual(response.status_code, 200)

    def test_context_summary(self):
        response = self.client.get(reverse('payment:summary'))
        self.assertIsInstance(response.context['acct_stmt'], AcctStmt)
        # User's current fund's balance show's in context
        self.assertIsNotNone(response.context['acct_stmts'][0].balance)
        # Other context
        self.assertIsInstance(response.context['acct_trans'][0], AcctTrans)
        self.assertIsInstance(response.context['acct_cost'], AcctCost)
        self.assertIsInstance(response.context['phone_numbers'][0], PhoneNumber)


class CardUpdateTests(TestCase):

    def setUp(self):
        # User Info
        self.password = PASSWORD
        self.hotel = create_hotel()
        # create "Hotel Manager" Group
        create._get_groups_and_perms()
        self.admin = create_hotel_user(hotel=self.hotel, username='admin', group='hotel_admin')
        # 2 Customers w/ 2 Cards each.
        self.customer = factory.customer()
        self.card = factory.card(customer_id=self.customer.id)
        self.card2 = factory.card(customer_id=self.customer.id)
        self.hotel.customer = self.customer
        self.hotel.save()
        # Login
        self.client.login(username=self.admin.username, password=PASSWORD)

    def tearDown(self):
        self.client.logout()

    def test_set_default_card_view(self):
        # default = False
        self.card.default = False
        self.card.save()
        self.assertFalse(self.card.default)
        # set to True
        response = self.client.get(reverse('payment:set_default_card',
            kwargs={'pk': self.card.id}), follow=True)
        self.assertRedirects(response, reverse('payment:card_list'))
        card = Card.objects.get(id=self.card.id)
        self.assertTrue(card.default)

    def test_delete_card_view(self):
        response = self.client.get(reverse('payment:delete_card',
            kwargs={'pk': self.card.id}), follow=True)
        self.assertRedirects(response, reverse('payment:card_list'))
        with self.assertRaises(Card.DoesNotExist):
            Card.objects.get(id=self.card.id)




'''Remove for the time being. Can add in V2 of the software. Not critical at 
this time.'''
# class OneTimePaymentTests(TestCase):

#     def setUp(self):
#         self.password = PASSWORD
#         self.hotel = create_hotel()
#         # create "Hotel Manager" Group
#         create._get_groups_and_perms()
#         # Users
#         self.admin = create_hotel_user(hotel=self.hotel, username='admin', group='hotel_admin')
#         # Stripe Card
#         self.card = factory.card()
#         self.hotel.customer = self.card.customer
#         self.hotel.save()
#         # Login
#         self.client.login(username=self.admin.username, password=PASSWORD)

#     def tearDown(self):
#         self.client.logout()

    ### OneTimePaymentView ###

    # def test_get_one_time_payment(self):
    #     response = self.client.get(reverse('payment:one_time_payment'))
    #     self.assertEqual(response.status_code, 200)

#     def test_create(self):
#         self.assertIsInstance(self.card, Card)
#         self.assertIsInstance(self.hotel.customer, Customer)

#     def test_response(self):
#         response = self.client.get(reverse('payment:one_time_payment'))
#         self.assertEqual(response.status_code, 200)

#     # For Attr's

#     def test_form(self):
#         response = self.client.get(reverse('payment:one_time_payment'))
#         self.assertIsInstance(response.context['form'], StripeOneTimePaymentForm)

#     def test_hotel(self):
#         response = self.client.get(reverse('payment:one_time_payment'))
#         self.assertEqual(response.context['form'].hotel, self.hotel)

#     def test_card_list(self):
#         response = self.client.get(reverse('payment:one_time_payment'))
#         self.assertTrue(response.context['form'].fields['cards'].choices)


class CardTests(TestCase):
    pass    


