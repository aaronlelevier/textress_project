from django import forms

from account.models import CHARGE_AMOUNTS


class StripeForm(forms.Form):
    stripe_token = forms.CharField()


class CardListForm(StripeForm):
    '''
    Card: Choose Existing Card, or Add a new one 
    '''
    add_card = forms.BooleanField(label='Add a Card',
        initial=False, required=False)


### TODO: May use the below "1x Pmt Form in the future?"

# class StripeOneTimePaymentForm(CardListForm):
#     '''
#     Amount: One-Time payment amount from Dropdown, or Choose an other amount

#     Card: Choose Existing Card, or Add a new one 
#     '''
#     def __init__(self, hotel, *args, **kwargs):
#         super(CardListForm, self).__init__(*args, **kwargs)
#         self.hotel = hotel
#         self.fields['cards'].choices = self._card_list

#     @property
#     def _card_list(self):
#         try: 
#             cards = self.hotel.customer.cards.all()
#         except AttributeError:
#             cards = None

#         if cards:
#             return [(c.id, c.last4) for c in cards]
#         else:
#             return [(None, None)]   
#     # Card List
#     cards = forms.ChoiceField(widget=forms.RadioSelect, required=False)
#     # Amount
#     amount = forms.ChoiceField(choices=CHARGE_AMOUNTS, required=False)
#     other = forms.BooleanField(label='Other Amount',
#         initial=False, required=False)
#     other_amount = forms.FloatField(required=False)
