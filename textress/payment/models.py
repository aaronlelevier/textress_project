import sys
import json
import stripe

from django.db import models
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

# from main.models import Hotel
from utils import email


class StripeClient(object):
    '''Stripe is needed for Model Manager Methods.'''

    def __init__(self, *args, **kwargs):
        super(StripeClient, self).__init__(*args, **kwargs)
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        self.stripe = stripe


class PmtAbstractBase(StripeClient, models.Model):
    """
    Add `stripe` attr to all Payment Models, and set Stripe API Key.

    `create` and `modified` Time Stamps for all Model changes.
    """
    short_pk = models.CharField(_("Short PK"), max_length=10, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created']

    def __str__(self):
        return self.id

    def save(self, *args, **kwargs):
        if self.id:
            self.short_pk = self._short_pk
        return super(PmtAbstractBase, self).save(*args, **kwargs)

    @property
    def _short_pk(self):
        '''Short PK used b/c don't want to expose the normal PK
        with Stripe Objects.'''
        return self.id[-10:]


############
# CUSTOMER #
############
class CustomerManager(StripeClient, models.Manager):

    def stripe_create(self, hotel, token, email):
        '''Always create the Stripe Customer first. Stripe Card second.'''
        try:
            stripe_customer = self.stripe.Customer.create(card=token,
                description=email, email=email)
        except self.stripe.error.InvalidRequestError:
            raise
        else:
            customer = Customer.objects.create(id=stripe_customer.id,
                email=email)
            hotel.update_customer(customer)
            return customer


class Customer(PmtAbstractBase):
    """
    Stripe Customer Object access point.
    """
    id = models.CharField(_("Stripe Customer ID"), primary_key=True, max_length=100)
    email = models.EmailField(_("Email"), blank=True)

    objects = CustomerManager()

    @property
    def stripe_object(self):
        "Returns the related Stripe Obj for the Model."
        return self.stripe.Customer.retrieve(self.id)

    def get_all_charges(self, limit=10, reverse=True):
        """
        Get all charges for a single customer.

        Returns a List of Dicts of Stripe Charges.
        """
        customer = self.stripe_object
        charges = [ch for ch in stripe.Charge.all(limit=limit, customer=customer.id).data]
        return sorted([json.loads(str(i)) for i in charges],
                      key=lambda k: k['created'], reverse=reverse)


########
# CARD #
########

class CardManager(StripeClient, models.Manager):

    def update_default(self, customer, id_):
        '''
        `customer` is a DB Obj
        `id_` is the "default card id"
        '''
        for card in self.exclude(id=id_):
            card.default = False
            card.save()

        # update `default card` on Stripe Customer Obj
        stripe_customer = self.stripe.Customer.retrieve(customer.id)
        stripe_customer.default_card = id_
        stripe_customer.save()

    def stripe_create(self, customer, token=None):
        '''Only Create Card DB instance. The Stripe Card Obj is already
        created.

        `token` arg: used to create new Card.
        '''
        try:
            stripe_customer = self.stripe.Customer.retrieve(customer.id)
            if token:
                stripe_card = stripe_customer.cards.create(card=token)
            else:
                stripe_card = stripe_customer.cards.retrieve(stripe_customer.default_card)
        except self.stripe.error.StripeError:
            raise
        else:
            return self.create(id=stripe_card.id, customer=customer,
                brand=stripe_card.brand, last4=stripe_card.last4,
                exp_month=stripe_card.exp_month, exp_year=stripe_card.exp_year)


class Card(PmtAbstractBase):
    # Keys
    customer = models.ForeignKey(Customer, related_name='cards')
    # Fields
    id = models.CharField(_("Stripe Card ID"), primary_key=True, max_length=100)
    brand = models.CharField(_("Brand"), max_length=25)
    last4 = models.PositiveIntegerField(_("Last 4"))
    exp_month = models.PositiveIntegerField(_("Exp Month"))
    exp_year = models.PositiveIntegerField(_("Exp Year"))
    # Semi-Auto Fields
    default = models.BooleanField(_("Default"), blank=True, default=True)
    # Auto Fields
    expires = models.CharField(_("Expires"), max_length=10, blank=True)

    objects = CardManager()

    def save(self, *args, **kwargs):
        '''When saving, if the card is the "default", update using the 
        model manager.'''
        # remove when not testing "sys.argv" check...
        if 'test' not in sys.argv:
            if self.default:
                Card.objects.update_default(customer=self.customer, id_=self.id)

        if self.exp_month and self.exp_year:
            self.expires = "{self.exp_month:02d}/{self.exp_year}".format(self=self)

        return super(Card, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        '''Delete Stripe Card b/4 deleting Model instance.'''

        if 'test' not in sys.argv:
            stripe_customer = self.stripe.Customer.retrieve(self.customer.id)
            stripe_customer.cards.retrieve(self.id).delete()

        return super(Card, self).delete(*args, **kwargs)
        
    def get_absolute_url(self):
        return reverse('payment:card_detail', kwargs={'pk': self.short_pk})

    @property
    def stripe_object(self):
        "Returns the related Stripe Obj for the Model."
        customer = self.stripe.Customer.retrieve(self.customer.id)
        return customer.cards.retrieve(self.id)


##########
# CHARGE #
##########

class ChargeManager(StripeClient, models.Manager):

    def stripe_create(self, hotel, card, customer, amount, email, currency='usd'):
        '''
        Create Charge based on Stripe Customer ID. Don't need a card token"
        because only charging existing Customers.
        '''
        # hotel = Hotel.objects.get(customer=customer)

        try:
            stripe_charge = self.stripe.Charge.create(customer=customer.id,
                amount=amount, currency=currency, description=email)
        except self.stripe.error.CardError:
            # Suspend Account
            subaccount = hotel.subaccount.update_status('suspended')
            # Send Email Notification of Suspended Account
            email.suspend_account(hotel)
            # TODO: Do I need to raise a form here, or do anything to alert Users
            # if they are accessing a View on their own that calls this method?
            raise
        else:
            hotel.subaccount.update_status('active')
            return self.create(card=card, customer=customer,
                id=stripe_charge.id, amount=stripe_charge.amount)


class Charge(PmtAbstractBase):
    # Keys
    card = models.ForeignKey(Card)
    customer = models.ForeignKey(Customer)
    # Fields
    id = models.CharField(_("Stripe Charge ID"), primary_key=True, max_length=100)
    amount = models.PositiveIntegerField(_("Stripe Amount"),
        help_text="Stripe Cost Amount of the Charge in cents. Ex: 2000 ~ $20")

    objects = ChargeManager()

    @property
    def stripe_object(self):
        "Returns the related Stripe Obj for the Model."
        return self.stripe.Customer.retrieve(self.id)


##########
# REFUND #
##########

class Refund(PmtAbstractBase):
    # Key
    charge = models.ForeignKey(Charge, related_name='refunds')
    # Fields
    id = models.CharField(_("Stripe Refund ID"), primary_key=True, max_length=100)
    amount = models.PositiveIntegerField(_("Stripe Amount"),
        help_text="Stripe Cost Amount of the Charge. Ex: 2000 ~ $20")

    @property
    def stripe_object(self):
        "Returns the related Stripe Obj for the Model."
        return self.stripe.Customer.retrieve(self.id)