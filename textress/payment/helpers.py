import stripe

from django.conf import settings

from .models import Customer, Card, Charge
from account.models import TransType, AcctTrans


stripe.api_key = settings.STRIPE_SECRET_KEY


def signup_register_step4(hotel, token, email, amount):
    '''Register Customer, Card, Charge.'''
    #DB create
    try:
        customer = Customer.objects.stripe_create(
            hotel=hotel, token=token, email=email)

        card = Card.objects.stripe_create(customer=customer)

        charge = Charge.objects.stripe_create(card=card,
            customer=customer, amount=amount, email=email)
            
    except stripe.error.StripeError:
        raise
    else:
        # make an AcctTrans record of 'funds_added' here
        trans_type = AcctTrans.objects.get(name='init_amt')
        acct_trans = AcctTrans.objects.create(hotel=self.hotel,
            trans_type=trans_type, amount=amount)

        return customer, card, charge








