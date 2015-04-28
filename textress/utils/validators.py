'''
Add regex, or some other validators for fields like phone number.
'''
from django.core.validators import BaseValidator
from django.utils.translation import ugettext, ugettext_lazy as _


class LengthValidator(BaseValidator):
    '''
    Not in use.
    '''
    compare = lambda self, a, b: a == b
    clean = lambda self, x: len(x)
    message = _(
        'Ensure this value has at least %(limit_value)d character (it has %(show_value)d).',
        'Ensure this value has at least %(limit_value)d characters (it has %(show_value)d).',
        'limit_value')
    code = 'length'