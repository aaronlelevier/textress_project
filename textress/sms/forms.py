from django import forms

from account.models import AcctTrans


class PhoneNumberAddForm(forms.Form):

    def __init__(self, hotel, *args, **kwargs):
        super(PhoneNumberAddForm, self).__init__(*args, **kwargs)
        self.hotel = hotel

    def clean(self):
        cd = super(PhoneNumberAddForm, self).clean()

        balance_ok = AcctTrans.objects.check_balance(self.hotel)
        if not balance_ok:
            raise forms.ValidationError("Please refill your account balance \
in order to process this transation.")

        return cd
