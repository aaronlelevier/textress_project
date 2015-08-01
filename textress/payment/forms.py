from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _

from account.models import CHARGE_AMOUNTS


class StripeForm(forms.Form):
    stripe_token = forms.CharField()
    amount = forms.ChoiceField(choices=CHARGE_AMOUNTS)