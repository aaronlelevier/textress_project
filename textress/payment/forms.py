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
        self.fields['amount'].initial = self.hotel.acct_cost.recharge_amt
        self.fields['auto_recharge'].initial = self.hotel.acct_cost.auto_recharge

    amount = forms.ChoiceField(choices=CHARGE_AMOUNTS, required=False)
    auto_recharge = forms.BooleanField(required=False)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount', None)
        try:
            return int(amount)
        except ValueError:
            raise forms.ValidationError("Not a valid 'amount'.")

    def clean_auto_recharge(self):
        auto_recharge = self.cleaned_data.get('auto_recharge', False)
        acct_cost = self.hotel.acct_cost

        if auto_recharge != acct_cost.auto_recharge:
            acct_cost.auto_recharge = auto_recharge
            acct_cost.save()

        return auto_recharge
