from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _

from utils.data import STATES


class StripeForm(forms.Form):
    stripe_token = forms.CharField()
