from django.conf import settings
from django.test import TestCase, TransactionTestCase
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from model_mommy import mommy

from account.models import (Pricing, AcctCost, AcctStmt, AcctTrans,
    CHARGE_AMOUNTS, BALANCE_AMOUNTS)
from account.tests.factory import (CREATE_ACCTCOST_DICT, create_acct_stmt,
    create_acct_stmts, create_acct_trans)
from main.models import Hotel
from main.tests.factory import (CREATE_USER_DICT, CREATE_HOTEL_DICT, PASSWORD,
    create_hotel, create_hotel_user)
from payment.forms import StripeForm
from payment.tests import factory
from payment.models import Customer, Card, Charge
from sms.models import PhoneNumber
from utils import create
from utils.email import Email


class RegistrationTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()

        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, group='hotel_admin')
        self.acct_cost = mommy.make(AcctCost, hotel=self.hotel)
        # Login
        self.client.login(username=self.user.username, password=PASSWORD)

    def test_register_step4_get(self):
        # Step 4
        response = self.client.get(reverse('payment:register_step4'))
        self.assertEqual(response.status_code, 200)
        
    def test_register_step4_context(self):
        # Step 4
        response = self.client.get(reverse('payment:register_step4'))
        self.assertIsInstance(response.context['form'], StripeForm)
        self.assertIsInstance(response.context['hotel'], Hotel)
        self.assertIsInstance(response.context['acct_cost'], AcctCost)
        self.assertTrue(response.context['months'])
        self.assertTrue(response.context['years'])
        self.assertTrue(response.context['PHONE_NUMBER_CHARGE'])
        self.assertContains(response, response.context['step'])
        self.assertContains(response, response.context['step_number'])

    def test_register_success(self):
        # valid Customer, so can access
        customer = mommy.make(Customer)
        hotel = Hotel.objects.first()
        hotel = hotel.update_customer(customer)
        response = self.client.get(reverse('payment:register_success'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, response.context['step'])
        self.assertContains(response, response.context['step_number'])

    def test_register_success_fail(self):
        self.client.logout()
        # random Admin User who hasn't paid gets redirected
        # Users
        hotel_b = create_hotel(name='hotel_b')
        admin_b = create_hotel_user(hotel=hotel_b, username='admin_b', group='hotel_admin')
        hotel_b = hotel_b.set_admin_id(user=admin_b)

        self.client.login(username=admin_b.username, password=PASSWORD)
        response = self.client.get(reverse('payment:register_success'))
        self.assertRedirects(response, reverse('payment:register_step4'))


class PaymentEmailTests(TestCase):
    
    def setUp(self):
        create._get_groups_and_perms()
        self.username = CREATE_USER_DICT['username']
        self.password = PASSWORD

        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel)
        self.client.login(username=self.username, password=self.password)

    def test_email(self):
        user = User.objects.first()
        customer = factory.customer()
        charge = factory.charge(customer.id)

        email = Email(
            to=user.email,
            from_email=settings.DEFAULT_EMAIL_BILLING,
            extra_context={
                'user': user,
                'customer': customer,
                'charge': charge
            },
            subject='email/payment_subject.txt',
            html_content='email/payment_email.html'
        )
        email.msg.send()


class BillingSummaryTests(TransactionTestCase):

    fixtures = ['trans_type.json']

    def setUp(self):
        # Users
        create._get_groups_and_perms()
        self.password = PASSWORD
        self.hotel = create_hotel()
        self.admin = create_hotel_user(hotel=self.hotel, username='admin', group='hotel_admin')
        self.user = create_hotel_user(hotel=self.hotel, username='user')
        # Billing Stmt Fixtures
        self.acct_cost, created = AcctCost.objects.get_or_create(self.hotel)
        self.acct_stmts = create_acct_stmts(self.hotel)
        self.acct_stmt = self.acct_stmts[-1]
        self.acct_trans = create_acct_trans(self.hotel)
        self.pricing = mommy.make(Pricing, hotel=self.hotel)
        self.phone_number = mommy.make(PhoneNumber, hotel=self.hotel)
        # Login
        self.client.login(username=self.admin.username, password=PASSWORD)

    def tearDown(self):
        self.client.logout()

    def test_get(self):
        response = self.client.get(reverse('payment:summary'))
        self.assertEqual(response.status_code, 200)

    def test_context(self):
        response = self.client.get(reverse('payment:summary'))
        self.assertIsInstance(response.context['acct_stmt'], AcctStmt)
        # User's current fund's balance show's in context
        self.assertIsNotNone(response.context['acct_stmts'][0].balance)
        # Other context
        self.assertIsInstance(response.context['acct_trans'][0], AcctTrans)
        self.assertIsInstance(response.context['acct_cost'], AcctCost)

    # acct_stmt table - current usage, starting balance, current balance

    def test_context_starting_balance_new_signup(self):
        """
        Starting balance (from previous month) should be 'zero' for new signups.
        """
        response = self.client.get(reverse('payment:summary'))

        self.assertIn("Starting Balance", response.content)
        self.assertEqual(response.context['acct_stmt_starting_balance'], 0)

    def test_context_funds_added(self):
        """
        Funds added for the month should be that month's 'init_amt' + 'recharge_amt' (s)
        """
        self.assertTrue(self.hotel.acct_trans.filter(
            trans_type__name__in=['recharge_amt', 'init_amt']).exists())

        response = self.client.get(reverse('payment:summary'))

        self.assertIn("Funds Added", response.content)
        self.assertEqual(response.context['acct_stmt'].funds_added, 0)

    def test_context_total_sms(self):
        response = self.client.get(reverse('payment:summary'))

        self.assertIn("SMS", response.content)
        self.assertEqual(
            response.context['acct_stmt'].total_sms,
            self.acct_stmt.total_sms
        )

    def test_context_total_sms_cost(self):
        self.acct_stmt.total_sms_costs = AcctStmt.objects.get_total_sms_costs(
            self.hotel, self.acct_stmt.total_sms)
        self.acct_stmt.save()

        response = self.client.get(reverse('payment:summary'))

        self.assertEqual(
            response.context['acct_stmt'].total_sms_costs,
            AcctStmt.objects.get_total_sms_costs(self.hotel, response.context['acct_stmt'].total_sms)
        )

    def test_context_phone_numbers(self):
        self.acct_stmt.phone_numbers = self.hotel.phone_numbers.count()
        self.acct_stmt.save()

        response = self.client.get(reverse('payment:summary'))

        self.assertIn("Phone Numbers", response.content)
        self.assertEqual(
            response.context['acct_stmt'].phone_numbers,
            self.acct_stmt.phone_numbers
        )

    def test_context_monthly_costs(self):
        """
        monthly_costs - just phone_number costs for the time being.
        """
        phone_numbers = self.hotel.phone_numbers.count()
        self.acct_stmt.monthly_costs = phone_numbers * settings.PHONE_NUMBER_MONTHLY_COST
        self.acct_stmt.save()

        response = self.client.get(reverse('payment:summary'))

        self.assertEqual(
            response.context['acct_stmt'].monthly_costs,
            self.acct_stmt.monthly_costs
        )

    def test_context_current_funds_balance(self):
        response = self.client.get(reverse('payment:summary'))

        self.assertIn("Current Funds Balance", response.content)
        self.assertEqual(
            response.context['acct_stmt'].balance,
            self.acct_stmt.balance
        )

    def test_acct_stmts_preview_none(self):
        [x.delete() for x in AcctStmt.objects.filter(hotel=self.hotel)]
        response = self.client.get(reverse('payment:summary'))
        self.assertFalse(response.context['acct_stmts'])
        self.assertFalse(response.context['acct_stmt'])

    def test_acct_stmts_preview_exist(self):
        today = timezone.now().date()
        create_acct_stmt(self.hotel, today.year, today.month)
        response = self.client.get(reverse('payment:summary'))
        self.assertTrue(response.context['acct_stmts'])
        self.assertTrue(response.context['acct_stmt'])


class CardUpdateTests(TestCase):

    def setUp(self):
        # User Info
        self.password = PASSWORD
        self.hotel = create_hotel()
        # create "Hotel Manager" Group
        create._get_groups_and_perms()
        self.admin = create_hotel_user(hotel=self.hotel, username='admin', group='hotel_admin')
        # 2 Customers w/ 2 Cards each.
        self.customer = factory.customer()
        self.card = factory.card(customer_id=self.customer.id)
        self.card2 = factory.card(customer_id=self.customer.id)
        self.hotel.customer = self.customer
        self.hotel.save()
        # Login
        self.client.login(username=self.admin.username, password=PASSWORD)

    def tearDown(self):
        self.client.logout()

    def test_card_list_response(self):
        response = self.client.get(reverse('payment:card_list'))
        self.assertEqual(response.status_code, 200)

    def test_card_list_context(self):
        response = self.client.get(reverse('payment:card_list'))
        self.assertTrue(response.context['form'])

    def test_card_list_billing_summary_breadcrumbs(self):
        # Also tests: ``BreadcrumbBaseMixin``
        response = self.client.get(reverse('payment:card_list'))
        self.assertTrue(response.context['breadcrumbs'])

    def test_set_default_card_view(self):
        # default = False
        self.card.default = False
        self.card.save()
        self.assertFalse(self.card.default)
        # set to True
        response = self.client.get(reverse('payment:set_default_card',
            kwargs={'pk': self.card.id}), follow=True)
        self.assertRedirects(response, reverse('payment:card_list'))
        card = Card.objects.get(id=self.card.id)
        self.assertTrue(card.default)
        # Success Message
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)

    def test_delete_card_view(self):
        response = self.client.get(reverse('payment:delete_card',
            kwargs={'pk': self.card.id}), follow=True)
        self.assertRedirects(response, reverse('payment:card_list'))
        with self.assertRaises(Card.DoesNotExist):
            Card.objects.get(id=self.card.id)
        # Success Message
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)


### COMMENT OUT:Remove for the time being. Can add in V2 of the software. Not critical at this time
# class OneTimePaymentTests(TestCase):

#     def setUp(self):
#         self.password = PASSWORD
#         self.hotel = create_hotel()
#         # create "Hotel Manager" Group
#         create._get_groups_and_perms()
#         # Users
#         self.admin = create_hotel_user(hotel=self.hotel, username='admin', group='hotel_admin')
#         # Stripe Card
#         self.card = factory.card()
#         self.hotel.customer = self.card.customer
#         self.hotel.save()
#         # Login
#         self.client.login(username=self.admin.username, password=PASSWORD)

#     def tearDown(self):
#         self.client.logout()

    ### OneTimePaymentView ###

    # def test_get_one_time_payment(self):
    #     response = self.client.get(reverse('payment:one_time_payment'))
    #     self.assertEqual(response.status_code, 200)

#     def test_create(self):
#         self.assertIsInstance(self.card, Card)
#         self.assertIsInstance(self.hotel.customer, Customer)

#     def test_response(self):
#         response = self.client.get(reverse('payment:one_time_payment'))
#         self.assertEqual(response.status_code, 200)

#     # For Attr's

#     def test_form(self):
#         response = self.client.get(reverse('payment:one_time_payment'))
#         self.assertIsInstance(response.context['form'], StripeOneTimePaymentForm)

#     def test_hotel(self):
#         response = self.client.get(reverse('payment:one_time_payment'))
#         self.assertEqual(response.context['form'].hotel, self.hotel)

#     def test_card_list(self):
#         response = self.client.get(reverse('payment:one_time_payment'))
#         self.assertTrue(response.context['form'].fields['cards'].choices)
