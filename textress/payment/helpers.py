import stripe

from django.conf import settings
from django.core.urlresolvers import reverse

from account.models import TransType, AcctTrans
from payment.models import Customer, Card, Charge
from utils import alert_messages


stripe.api_key = settings.STRIPE_SECRET_KEY


def signup_register_step4(hotel, token, email, amount):
    '''
    Setup all Payment records for the Hotel upon registration.

    Register Customer, Card, Charge.
    '''
    try:
        # Payment.model records
        customer = Customer.objects.stripe_create(
            hotel=hotel, token=token, email=email)

        card = Card.objects.stripe_create(customer=customer)

        charge = Charge.objects.stripe_create(
            hotel=hotel, amount=amount)
            
    except stripe.error.StripeError:
        raise

    return customer, card, charge


def no_funds_alert():
    return {
        'type': 'danger',
        'link': reverse('payment:one_time_payment'),
        'strong_message': 'Alert!',
        'message': alert_messages['no_funds_alert']
    }


def no_customer_alert():
    return {
        'type': 'danger',
        'link': reverse('payment:one_time_payment'),
        'strong_message': 'Alert!',
        'message': alert_messages['no_customer_alert']
    }
