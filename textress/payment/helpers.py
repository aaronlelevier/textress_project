import stripe

from django.conf import settings

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

        charge = Charge.objects.stripe_create(hotel=hotel, card=card,
            customer=customer, amount=amount, email=email)
            
    except stripe.error.StripeError:
        raise

    else:
        # Account.model records for individual transactions
        # recorded for ``accounting`` purposes
        trans_type = TransType.objects.get(name='init_amt')
        
        acct_trans = AcctTrans.objects.create(hotel=hotel,
            trans_type=trans_type, amount=amount)

        return customer, card, charge