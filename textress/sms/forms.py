from django import forms

from account.models import AcctTrans
from utils.exceptions import AutoRechargeOffExcp
from utils.forms import Bootstrap3Form


class PhoneNumberAddForm(Bootstrap3Form):

    def __init__(self, hotel, *args, **kwargs):
        super(PhoneNumberAddForm, self).__init__(*args, **kwargs)
        self.hotel = hotel

    def clean(self):
        cd = super(PhoneNumberAddForm, self).clean()
        try:
            AcctTrans.objects.check_balance(self.hotel)
        except AutoRechargeOffExcp:
            raise forms.ValidationError("Form Error")
        return cd
