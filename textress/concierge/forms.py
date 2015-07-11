from djangular.forms import NgFormValidationMixin
from djangular.styling.bootstrap3.forms import Bootstrap3ModelForm

from concierge.models import Guest


class GuestForm(NgFormValidationMixin, Bootstrap3ModelForm):

    form_name = 'guest_form'
    
    class Meta:
        model = Guest
        fields = ['name', 'room_number', 'phone_number', 'check_in', 'check_out']