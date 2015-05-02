import random
from string import digits

from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import Group
from django.core.mail import send_mail, EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string

from account.models import AcctStmt


login_messages = {
    'now_logged_in': 'You are now logged in',
    'no_match': 'Please check username and password',
    'no_register': 'Please use a valid username, email, and password',
    'not_active': "Your account hasn't been activated. Please check your email in order \
    to activate your account.",
    'activate_via_email': 'Please check your email in order to activate your account.',
    'account_active': 'Your account has been successfully activated. Please Login.',
    'username_taken': 'Username already taken',
    'email_taken': 'Email already taken.',
    'invalid_username': 'Invalid Username',
    'no_email_match': 'No account matching that email.',
    'no_username_match': 'Username misspelled or not registered. Please try again.',
    'login_error': 'Login unsuccessful. Please try again.',
    'passwords_dont_match': 'Passwords do not match',
    'password_has_reset': 'Your password has been reset. You are now logged in.',
    'reset_pw_sent': 'Temporary password sent. Please check your email.',
    'hotel_not_found': "The Hotel that you were trying to reach could not be found. \
    Please contact their main phone number. Thank you."
    }


def salt(length=7):
    return "".join([random.choice(digits) for x in range(length)])


def add_group(user, group):
    group = Group.objects.get(name=group)
    user.groups.add(group)
    user.save()
    return user