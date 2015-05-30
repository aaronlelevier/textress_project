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

from account.models import AcctCost
from account.tests.factory import CREATE_ACCTCOST_DICT
from main.models import Hotel
from main.tests.test_models import create_hotel
from main.tests.factory import CREATE_USER_DICT, CREATE_HOTEL_DICT
from payment.models import Customer, Card, Charge
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
        self.assertContains(response.context['acct_cost'])
        self.assertContains(response.context['step'])
        self.assertContains(response.context['step_number'])
        self.assertContains(response.context['months'])
        self.assertContains(response.context['years'])
        self.assertContains(response.context['PHONE_NUMBER_CHARGE'])


class PaymentEmailTests(TestCase):
    
    def setUp(self):
        create._get_groups_and_perms()
        self.username = CREATE_USER_DICT['username']
        self.password = '1234'

        # Step 1
        response = self.client.post(reverse('main:register_step1'),
            CREATE_USER_DICT)
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


# class CardTests(TestCase):

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

#         # Stripe
#         self.customer = mommy.make(Customer)
#         self.hotel.customer = self.customer
#         self.hotel.admin_id = self.admin.id
#         self.hotel.save()

#         self.cards = mommy.make(Card, customer=self.customer, _quantity=3)
#         self.card = self.cards[0]

#     def test_create(self):
#         assert isinstance(self.hotel, Hotel)
#         assert isinstance(self.card, Card)

#         assert self.mgr.profile.hotel == self.hotel
#         assert self.user.profile.hotel == self.hotel
#         assert self.hotel.admin_id == self.admin.id

#         assert len(self.cards) == 3
#         for card in self.cards:
#             assert card.customer == self.hotel.customer


#     def test_list_loggedOut(self):
#         # Not Logged in can't access
#         response = self.client.get('payment:card_list')
#         response.status_code == 302

#     def test_list_admin(self):
#         # Admin has full access
#         self.client.login(username=self.admin.username, password=self.password)
#         response = self.client.get('payment:card_list')
#         response.status_code == 200

#     def test_list_mgr(self):
#         # Mgr Can't Access
#         self.client.login(username=self.mgr.username, password=self.password)
#         response = self.client.get('payment:card_list')
#         response.status_code == 404

#     def test_list_user(self):
#         # User Can't Access
#         self.client.login(username=self.user.username, password=self.password)
#         response = self.client.get('payment:card_list')
#         response.status_code == 404

#     def test_detail(self):
#         ### Other Users can't Login Fail tests ###

#         # User Can't Access
#         self.client.login(username=self.user.username, password=self.password)
#         response = self.client.get(reverse('payment:card_detail', kwargs={'pk': self.card.short_pk}))
#         response.status_code == 404

#         # Mgr Can't Access
#         self.client.logout()
#         self.client.login(username=self.mgr.username, password=self.password)
#         response = self.client.get(reverse('payment:card_detail', kwargs={'pk': self.card.short_pk}))
#         response.status_code == 404

#         # Mgr Can't Access
#         self.client.logout()
#         self.client.login(username=self.other_admin.username, password=self.password)
#         response = self.client.get(reverse('payment:card_detail', kwargs={'pk': self.card.short_pk}))
#         response.status_code == 404

#         ### Real Tests of View w/ Authenticated Admin ###

#         # Admin has full access
#         self.client.login(username=self.admin.username, password=self.password)
#         response = self.client.get(reverse('payment:card_detail', kwargs={'pk': self.card.short_pk}))
#         assert response.status_code == 200

#         # Get the Object
#         print(response.context['object'])
#         assert response.context['object'] == self.card

#     def test_update(self):
#         # Admin has full access
#         self.client.login(username=self.admin.username, password=self.password)
#         response = self.client.get(reverse('payment:card_update', kwargs={'pk': self.card.short_pk}))
#         assert response.status_code == 200

#         # Set a card to Default=False, then use the UpdateView to change it
#         card = self.cards[1]
#         card.default = False
#         card.save()
#         assert not card.default

#         response = self.client.post(reverse('payment:card_update', kwargs={'pk': card.short_pk}),
#             {'default': True}, follow=True)
#         updated_card = Card.objects.get(short_pk=card.short_pk)
#         assert updated_card.default
#         self.assertRedirects(response, reverse('payment:card_detail', kwargs={'pk': card.short_pk}))


#     def test_delete(self):
#         # Admin has full access
#         self.client.login(username=self.admin.username, password=self.password)
#         response = self.client.get(reverse('payment:card_delete', kwargs={'pk': self.card.short_pk}))
#         assert response.status_code == 200

#         # 3 Cards exist b/4 deleteting 1 via the View, then only 2 exist
#         assert len(Card.objects.all()) == 3
#         response = self.client.post(reverse('payment:card_delete', kwargs={'pk': self.cards[-1].short_pk}),
#             follow=True)
#         assert len(Card.objects.all()) == 2
#         self.assertRedirects(response, reverse('payment:card_list'))