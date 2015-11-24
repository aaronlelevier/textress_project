from django import forms

from account.models import CHARGE_AMOUNTS
from utils.forms import Bootstrap3Form


class StripeForm(forms.Form):
    stripe_token = forms.CharField()


class CardListForm(StripeForm):
    '''
    Card: Choose Existing Card, or Add a new one 
    '''
    add_card = forms.BooleanField(label='Add a Card',
        initial=False, required=False)


class OneTimePaymentForm(Bootstrap3Form):
    '''
    Amount: One-Time payment amount from Dropdown, or Choose an other amount

    Card: Choose Existing Card, or Add a new one 
    '''
    def __init__(self, hotel, *args, **kwargs):
        super(OneTimePaymentForm, self).__init__(*args, **kwargs)
        self.hotel = hotel
        self.fields['auto_pay'].initial = self.hotel.acct_cost.auto_recharge

    amount = forms.ChoiceField(choices=CHARGE_AMOUNTS, required=False)
    auto_pay = forms.BooleanField()
