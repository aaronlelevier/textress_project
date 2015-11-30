from django import forms 
from django.contrib.auth import forms as auth_forms

from djangular.forms import NgFormValidationMixin

from account.models import AcctCost
from utils.forms import Bootstrap3Form, Bootstrap3ModelForm

#################
# DEFAULT FORMS #
#################

class AcctCostForm(Bootstrap3ModelForm):
    # djangular req
    form_name = 'acct_cost_create_form'

    class Meta:
        model = AcctCost
        fields = ['init_amt', 'balance_min', 'recharge_amt', 'auto_recharge']


class AcctCostUpdateForm(Bootstrap3ModelForm):
    # djangular req
    form_name = 'acct_cost_update_form'

    class Meta:
        model = AcctCost
        fields = ['balance_min', 'recharge_amt', 'auto_recharge']
        

########
# AUTH #
########

class AuthenticationForm(auth_forms.AuthenticationForm, Bootstrap3Form):
    form_name = 'login_form'


class PasswordResetForm(auth_forms.PasswordResetForm, Bootstrap3Form):
    form_name = 'pw_reset_form'


class SetPasswordForm(auth_forms.SetPasswordForm, Bootstrap3Form):
    form_name = 'set_pw_form'


class PasswordChangeForm(auth_forms.PasswordChangeForm, Bootstrap3Form):
    form_name = 'pw_change_form'


##############
# CLOSE ACCT #
##############

class CloseAccountForm(forms.Form):
    pass 


class CloseAcctConfirmForm(forms.Form):
    pass