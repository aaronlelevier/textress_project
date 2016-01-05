from django.conf import settings
from django.test import TestCase

from model_mommy import mommy

from account.models import AcctCost
from main.tests.factory import create_hotel, create_hotel_user
from payment.tests.factory import charge, customer
from utils import create, email
from utils.email import Email


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
        email.send_charge_failed_email(self.hotel, _charge.amount)
