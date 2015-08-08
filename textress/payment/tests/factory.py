import stripe

from django.conf import settings

from model_mommy import mommy

from payment.models import StripeClient, Customer, Card, Charge, Refund

# Set Stripe Key for All tests
stripe.api_key = settings.STRIPE_SECRET_KEY


### Customer

def stripe_customer(customer_id=None):
    if customer_id:
        return stripe.Customer.retrieve(customer_id)
    else:
        count_ = Customer.objects.count()
        return stripe.Customer.all(limit=count_+1).data[count_]

def customer(customer_id=None):
    if not customer_id:
        customer_id = stripe_customer().id
    customer, created = Customer.objects.get_or_create(id=customer_id)
    return customer


### Card

def stripe_card(customer_id=None):
    sc = stripe_customer(customer_id)
    return sc.sources.retrieve(sc.cards.data[0].id)

def card(customer_id=None):
    _customer = customer(customer_id)
    sc = stripe_card(customer_id)
    card, created = Card.objects.get_or_create(
        customer=_customer,
        id=sc.id,
        brand=sc.brand,
        last4=sc.last4,
        exp_month=sc.exp_month,
        exp_year=sc.exp_year
    )
    return card


### Charge

def stripe_charge(customer_id=None):
    _customer = customer(customer_id)
    charge_id = _customer.get_all_charges()[0]['id']
    return stripe.Charge.retrieve(charge_id)

def charge(customer_id=None):
    _customer = customer(customer_id)
    sc = stripe_charge(customer_id=_customer.id)
    charge, created = Charge.objects.get_or_create(
        card=card(_customer.id),
        customer=_customer,
        id=sc.id,
        amount=sc.amount
    )
    return charge


### Refunds

def stripe_refund(customer_id=None):
    charge = stripe_charge(customer_id)
    try:
        sr = charge.refunds[0]
    except IndexError:
        sr = None
    finally:
        return sr

def refund(customer_id=None):
    sr = stripe_refund(customer_id)
    if sr:
        charge = stripe_charge(customer_id)
        refund, created = Refund.objects.get_or_create(
            charge=charge,
            id=sr.id,
            amount=sr.amount
        )
    else:
        refund = None
    return refund
