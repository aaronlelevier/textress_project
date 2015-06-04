from django import forms
from django.conf import settings


class PhoneNumberForm(forms.Form):

    def __init__(self, phone_numbers, *args, **kwargs):
        super(PhoneNumberForm, self).__init__(*args, **kwargs)

        # attach PhoneNumbers to Form
        self.phone_numbers = phone_numbers
        self.fields['phone_number'] = forms.RadioSelect(
            choices=[(ph.sid, ph.friendly_name) for ph in self.phone_numbers])


class PhoneNumberSelectForm(forms.Form):
    "Display 10 Available Twilio PhoneNumber Obj, and add to cookie."

    # PHONES = (
    #     ('area_code','Find a phone number based on the area code of the Hotel'),
    #     ('contains', "Find a phone number starting with certain #'s"),
    #     ('contains', "Find a phone number mathcing a pattern")
    #     )
    # radio = forms.ChoiceField(choices=PHONES)

    def __init__(self, request, twilio_hotel, *args, **kwargs):
        super(PhoneNumberSelectForm, self).__init__(*args, **kwargs)

        # attach Available PhoneNumbers to Form
        self.request = request
        self.phone_numbers = twilio_hotel.available_phone_numbers()
        self.fields['phone_number'] = forms.ChoiceField(widget=forms.RadioSelect(),
            choices=[(ph.phone_number, ph.friendly_name) for ph in self.phone_numbers])

        def clean(self):
            cleaned_data = super(PhoneNumberSelectForm, self).clean()

            phone_number = cleaned_data.get("phone_number")
            self.request.session['phone_number'] = phone_number
            print('form cookie', self.request.session['phone_number'])
            return cleaned_data


# class PhoneNumberBuyForm(forms.Form):

            

class PhoneNumberAddForm(forms.Form):
    "No fields. Just accept a POST action, and create PhoneNumber Obj."
    pass