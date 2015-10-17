from django import forms

from djangular.styling.bootstrap3.forms import (Bootstrap3Form,
    Bootstrap3ModelForm)


class EmptyForm(forms.Form):
    "Placeholder form for 'Confirm' action form pages."
    pass


class Bootstrap3Form(Bootstrap3Form):
    required_css_class = 'required'


class Bootstrap3ModelForm(Bootstrap3ModelForm):
    required_css_class = 'required'