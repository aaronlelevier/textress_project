from django.conf import settings
from django.test import TestCase

from django.core.mail import EmailMultiAlternatives

from utils.email import Email


class EmailTests(TestCase):

    def setUp(self):
        self.email = Email(
            to=settings.DEFAULT_EMAIL_AARON,
            subject='email/payment_subject.txt',
            html_content='email/payment_email.html'
            )

    def test_create(self):
        assert isinstance(self.email, Email)

    def test_content(self):
        assert hasattr(self.email, 'html_content')
        assert hasattr(self.email, 'text_content')

    def test_msg(self):
        assert isinstance(self.email.msg, EmailMultiAlternatives)


'''
Manual email tests, ignored by test runner. Because doesn't send 
email while running `unittest`.
'''

def try_send():
    email = Email(
        to=settings.DEFAULT_EMAIL_AARON,
        subject='email/coming_soon_subject.txt',
        html_content='email/coming_soon_email.html'
        )
    return email.msg.send()