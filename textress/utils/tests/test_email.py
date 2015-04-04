import pytest

from django.core.mail import send_mail
from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import Group, Permission, User

from django.core.mail import (send_mail, EmailMessage, EmailMultiAlternatives,
    get_connection)

from model_mommy import mommy

from utils.email import Email
from contact.models import Newsletter


class EmailTests(TestCase):

    def setUp(self):
        self.email = Email(
            to=settings.DEFAULT_EMAIL_ADMIN,
            subject='email/coming_soon_subject.txt',
            html_content='email/coming_soon_email.html'
            )

    def test_create(self):
        assert isinstance(self.email, Email)

    def test_content(self):
        assert hasattr(self.email, 'html_content')
        assert hasattr(self.email, 'text_content')

    def test_msg(self):
        assert isinstance(self.email.msg, EmailMultiAlternatives)


# class SendEmailTests(object):
#     '''
#     Manual email tests, ignored by test runner. Because doesn't send 
#     email while running `unittest`.
#     '''
#     def __init__(self):
#         self.hotel = Hotel.objects.get(name="Dave Hotel")
#         self.user = User.objects.get(username="dave")

#     def try_send_suspend_email(self):
#         return email.send_suspend_email(self.hotel)

#     def try_send_close_account_email(self):
#         return email.send_close_account_email(self.user)

#     def try_send_forgot_password_email(self):
#         return email.send_forgot_password_email(self.user, temp_password='1234')

#     def try_send_contact_email(self):
#         contact = Contact.objects.filter(email='pyaaron@gmail.com')[0]
#         return email.send_contact_email(contact)

        

# class EmailAddressTests(TestCase):

#     def test_admin(self):
#         # Only change `from_email`
#         emails = [settings.DEFAULT_EMAIL_ADMIN,
#             settings.DEFAULT_EMAIL_SUPPORT,
#             settings.DEFAULT_EMAIL_BILLING
#             ]

#         # Defaults
#         for from_email in emails:
#             subject = "Message from the {}".format(from_email)
#             message = subject
#             recipient_list = ['pyaaron@gmail.com']
#             msg = send_mail(subject,
#                 message,
#                 from_email,
#                 recipient_list,
#                 auth_user=from_email,
#                 auth_password=settings.EMAIL_HOST_PASSWORD
#                 )
#             assert msg == 1

#     def test_two(self):
#         user = User.objects.first()
#         return send_mail('hi', 'from TestCase msg', settings.DEFAULT_EMAIL_ADMIN,
#             ['pyaaron@gmail.com'], auth_user=settings.DEFAULT_EMAIL_ADMIN,
#             auth_password=settings.EMAIL_HOST_PASSWORD)

