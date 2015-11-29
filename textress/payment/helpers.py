import stripe

from django.conf import settings
from django.core.urlresolvers import reverse

from payment.models import Customer, Card, Charge
from account.models import TransType, AcctTrans


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
        'message': "SMS sending and receiving has been deactivated. Please \
contact your system admin to reactivate the account. This is most likely due to insufficient funds."
    }
