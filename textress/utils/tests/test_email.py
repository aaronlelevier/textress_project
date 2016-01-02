from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.test import TestCase
from django.template.loader import render_to_string
from django.utils import html

from model_mommy import mommy

from account.models import AcctCost
from main.tests.factory import create_hotel, create_hotel_user
from payment.tests.factory import charge, customer
from utils import create, email
from utils.email import Email


class EmailTests(TestCase):

    def setUp(self):
        self.email = Email(
            to=settings.DEFAULT_EMAIL_AARON,
            subject='email/payment_subject.txt',
            html_content='email/payment_email.html'
            )

    def test_create(self):
        self.assertIsInstance(self.email, Email)

    def test_content(self):
        self.assertTrue(hasattr(self.email, 'html_content'))
        self.assertTrue(hasattr(self.email, 'text_content'))

    def test_msg(self):
        self.assertIsInstance(self.email.msg, EmailMultiAlternatives)


class ChargeFailedEmailTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, group='hotel_admin')
        self.amount = 500

    def test_context(self):
        context = {
            'user': self.admin,
            'amount': self.amount,
            'SITE': settings.SITE
        }

        ret = html.strip_tags(render_to_string('email/charge_failed/email.html', context))

        self.assertIn("Hello {},".format(self.admin), ret)
        self.assertIn("Charge failed for ${:.2f}".format(self.amount/100.0), ret)
        self.assertIn("{}/billing/manage-payment-methods/".format(settings.SITE), ret)


class LiveEmailTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, group="hotel_admin")
        self.user.email = settings.DEFAULT_FROM_EMAIL
        self.user.save()

    def test_send_email(self):
        email = Email(
            to=settings.DEFAULT_EMAIL_AARON,
            subject='email/delete_unknown_number_failed/subject.txt',
            html_content='email/delete_unknown_number_failed/email.html'
            )
        return email.msg.send()

    def test_send_auto_recharge_failed_email(self):
        mommy.make(AcctCost, hotel=self.hotel)
        # send
        email.send_auto_recharge_failed_email(self.hotel)

    def test_send_account_charged_email(self):
        _customer = customer()
        self.hotel.update_customer(_customer)
        _charge = charge(_customer.id)
        # send
        email.send_account_charged_email(self.hotel, _charge)

    def test_send_charge_failed_email(self):
        _customer = customer()
        self.hotel.update_customer(_customer)
        _charge = charge(_customer.id)
        # send
        email.send_charge_failed_email(self.hotel, 1000)
