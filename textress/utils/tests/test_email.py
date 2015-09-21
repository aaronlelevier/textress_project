from django.conf import settings
from django.test import TestCase
from django.core.mail import EmailMultiAlternatives

from model_mommy import mommy

from account.models import AcctTrans, AcctCost
from main.tests.factory import create_hotel, create_hotel_user
from payment.tests.factory import charge, customer
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
Email Test Sends
----------------
Manual email tests, ignored by test runner. Because doesn't send 
email while running `unittest`.
'''

def test_send_email():
    email = Email(
        to=settings.DEFAULT_EMAIL_AARON,
        subject='email/coming_soon_subject.txt',
        html_content='email/coming_soon_email.html'
        )
    return email.msg.send()


def test_send_auto_recharge_failed_email():
    # setup
    hotel = create_hotel()
    user = create_hotel_user(hotel, group="hotel_admin")
    user.email = settings.DEFAULT_FROM_EMAIL
    user.save()
    mommy.make(AcctCost, hotel=hotel)
    # send
    AcctTrans.objects.send_auto_recharge_failed_email(hotel)


def test_send_account_charged_email():
    # setup
    hotel = create_hotel()
    user = create_hotel_user(hotel, group="hotel_admin")
    user.email = settings.DEFAULT_FROM_EMAIL
    user.save()
    _customer = customer()
    hotel.update_customer(_customer)
    _charge = charge(_customer.id)
    # send
    AcctTrans.objects.send_account_charged_email(hotel, _charge)


def test_send_charge_failed_email():
    # setup
    hotel = create_hotel()
    user = create_hotel_user(hotel, group="hotel_admin")
    user.email = settings.DEFAULT_FROM_EMAIL
    user.save()
    _customer = customer()
    hotel.update_customer(_customer)
    _charge = charge(_customer.id)
    # send
    AcctTrans.objects.send_charge_failed_email(hotel, 1000)