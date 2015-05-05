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

from ..models import Customer, Card
from main.models import Hotel
from main.tests.test_models import create_hotel
from utils import create



class CardTests(TestCase):

    def setUp(self):
        self.password = '1234'
        self.hotel = create_hotel()
        self.other_hotel = create_hotel('other')

        # create "Hotel Manager" Group
        create._get_groups_and_perms()

        # Admin
        self.admin = mommy.make(User, username='admin')
        self.admin.groups.add(Group.objects.get(name="hotel_admin"))
        self.admin.set_password(self.password)
        self.admin.save()
        self.admin.profile.update_hotel(hotel=self.hotel)

        # Manager
        self.mgr = mommy.make(User, username='mgr')
        self.mgr.groups.add(Group.objects.get(name="hotel_manager"))
        self.mgr.set_password(self.password)
        self.mgr.save()
        self.mgr.profile.update_hotel(hotel=self.hotel)

        # User
        self.user = mommy.make(User, username='user')
        self.user.set_password(self.password)
        self.user.save()
        self.user.profile.update_hotel(hotel=self.hotel)

        # Other Hotel Admin
        self.other_admin = mommy.make(User, username='other_admin')
        self.other_admin.groups.add(Group.objects.get(name="hotel_admin"))
        self.other_admin.set_password(self.password)
        self.other_admin.save()
        self.other_admin.profile.update_hotel(hotel=self.other_hotel)

        # Stripe
        self.customer = mommy.make(Customer)
        self.hotel.customer = self.customer
        self.hotel.admin_id = self.admin.id
        self.hotel.save()

        self.cards = mommy.make(Card, customer=self.customer, _quantity=3)
        self.card = self.cards[0]

    def test_create(self):
        assert isinstance(self.hotel, Hotel)
        assert isinstance(self.card, Card)

        assert self.mgr.profile.hotel == self.hotel
        assert self.user.profile.hotel == self.hotel
        assert self.hotel.admin_id == self.admin.id

        assert len(self.cards) == 3
        for card in self.cards:
            assert card.customer == self.hotel.customer


    def test_list_loggedOut(self):
        # Not Logged in can't access
        response = self.client.get('payment:card_list')
        response.status_code == 302

    def test_list_admin(self):
        # Admin has full access
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get('payment:card_list')
        response.status_code == 200

    def test_list_mgr(self):
        # Mgr Can't Access
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get('payment:card_list')
        response.status_code == 404

    def test_list_user(self):
        # User Can't Access
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get('payment:card_list')
        response.status_code == 404



    def test_detail(self):
        ### Other Users can't Login Fail tests ###

        # User Can't Access
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('payment:card_detail', kwargs={'pk': self.card.short_pk}))
        response.status_code == 404

        # Mgr Can't Access
        self.client.logout()
        self.client.login(username=self.mgr.username, password=self.password)
        response = self.client.get(reverse('payment:card_detail', kwargs={'pk': self.card.short_pk}))
        response.status_code == 404

        # Mgr Can't Access
        self.client.logout()
        self.client.login(username=self.other_admin.username, password=self.password)
        response = self.client.get(reverse('payment:card_detail', kwargs={'pk': self.card.short_pk}))
        response.status_code == 404

        ### Real Tests of View w/ Authenticated Admin ###

        # Admin has full access
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('payment:card_detail', kwargs={'pk': self.card.short_pk}))
        assert response.status_code == 200

        # Get the Object
        print(response.context['object'])
        assert response.context['object'] == self.card

    def test_update(self):
        # Admin has full access
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('payment:card_update', kwargs={'pk': self.card.short_pk}))
        assert response.status_code == 200

        # Set a card to Default=False, then use the UpdateView to change it
        card = self.cards[1]
        card.default = False
        card.save()
        assert not card.default

        response = self.client.post(reverse('payment:card_update', kwargs={'pk': card.short_pk}),
            {'default': True}, follow=True)
        updated_card = Card.objects.get(short_pk=card.short_pk)
        assert updated_card.default
        self.assertRedirects(response, reverse('payment:card_detail', kwargs={'pk': card.short_pk}))


    def test_delete(self):
        # Admin has full access
        self.client.login(username=self.admin.username, password=self.password)
        response = self.client.get(reverse('payment:card_delete', kwargs={'pk': self.card.short_pk}))
        assert response.status_code == 200

        # 3 Cards exist b/4 deleteting 1 via the View, then only 2 exist
        assert len(Card.objects.all()) == 3
        response = self.client.post(reverse('payment:card_delete', kwargs={'pk': self.cards[-1].short_pk}),
            follow=True)
        assert len(Card.objects.all()) == 2
        self.assertRedirects(response, reverse('payment:card_list'))






