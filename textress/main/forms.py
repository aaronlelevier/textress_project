from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext, ugettext_lazy as _

from djangular.forms import NgFormValidationMixin
from djangular.styling.bootstrap3.forms import Bootstrap3ModelForm

from concierge.models import validate_phone
from main.models import Hotel
from utils import ph_formatter


class UserCreateForm(Bootstrap3ModelForm):
    '''
    Form used during Registration to Create the Admin User.
    '''
    # djangular req
    form_name = 'user_create_form'

    # UserCreationForm
    error_messages = {
        'duplicate_username': _("A user with that username already exists."),
        'password_mismatch': _("The two password fields didn't match."),
    }

    # because I want to require these fields, and the Django model
    # doesn't require them by default
    first_name = forms.CharField(label=_("First Name"), required=True)
    last_name = forms.CharField(label=_("Last Name"), required=True)
    email = forms.EmailField(label=_("Email"), required=True)

    username = forms.RegexField(label=_("Username"), max_length=30,
        regex=r'^[\w.@+-_]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Confirm Password"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email',
            'username', 'password1', 'password2',)

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )
        return password2

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserUpdateForm(Bootstrap3ModelForm):
    '''
    Form used during Registration to Update the Admin User.
    '''
    # djangular req
    form_name = 'admin_update_form'

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']


class HotelCreateForm(Bootstrap3ModelForm):
    # djangular req
    form_name = 'hotel_create_form'

    error_messages = {
        'invalid_ph':_('Please enter a 10-digit phone number'),
    }

    address_phone = forms.RegexField(r'^(\d{3})-(\d{3})-(\d{4})$',
        label='Phone number',
        error_messages={'invalid': 'Phone number have 10 digits'},
        help_text='Allowed phone number format: 702-510-5555')

    class Meta:
        model = Hotel
        fields = ['name', 'address_phone', 'address_line1', 'address_line2',
            'address_city', 'address_state', 'address_zip']

    def __init__(self, hotel=None, *args, **kwargs):
        super(HotelCreateForm, self).__init__(*args, **kwargs)

        try:
            address_phone = hotel.address_phone
        except AttributeError:
            self.initial['address_phone'] = ""
        else:
            self.initial['address_phone'] = ph_formatter(getattr(hotel, 'address_phone', None))

    def clean_address_phone(self):
        """
        Return the Twilio formatted PH #
        """
        self.cleaned_data = super(HotelCreateForm, self).clean()

        address_phone = self.cleaned_data.get('address_phone')

        # returns a validated and formatted phone # ex: "+17025108888"
        # all phone #'s saved to the DB in this format
        phone = validate_phone(address_phone)

        if Hotel.objects.filter(address_phone=phone).exists():
            raise forms.ValidationError("Hotel phone number exists.")

        return phone



