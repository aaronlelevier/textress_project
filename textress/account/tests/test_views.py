import datetime

from django.conf import settings
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, Group

from model_mommy import mommy

from account.forms import AcctCostForm
from account.models import (AcctStmt, TransType, AcctTrans, AcctCost,
    Pricing, CHARGE_AMOUNTS, BALANCE_AMOUNTS)
from account.tests.factory import (create_acct_stmts, create_acct_stmt,
    create_acct_trans, CREATE_ACCTCOST_DICT)
from main.models import Hotel
from main.tests.factory import (create_hotel, create_hotel_user, make_subaccount,
    make_subaccount_live, CREATE_USER_DICT, CREATE_HOTEL_DICT, PASSWORD)
from payment.models import Customer
from sms.models import PhoneNumber
from utils import create, login_messages, alert_messages


class AccountTests(TestCase):
    # Test Rending of view, template path is correct, url
    # User of each permission type needed

    def setUp(self):
        create._get_groups_and_perms()
        self.password = PASSWORD

        self.hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, 'admin', 'hotel_admin')
        self.manager = create_hotel_user(self.hotel, 'manager', 'hotel_manager')
        self.user = create_hotel_user(self.hotel, 'user')

        self.ph = mommy.make(PhoneNumber, hotel=self.hotel)
        self.hotel.update_twilio_phone(self.ph.sid, self.ph.phone_number)

        self.customer = mommy.make(Customer)
        self.hotel.update_customer(self.customer)

    # private

    def test_private(self):
        self.client.login(username=self.user.username, password=self.password)

        response = self.client.get(reverse('private'), follow=True)

        self.assertRedirects(response, reverse('account'))
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        self.assertEqual(str(m[0]), login_messages['now_logged_in'])

    def test_private__logged_out(self):
        response = self.client.get(reverse('private'), follow=True)

        self.assertRedirects(response, "{}?next={}".format(reverse('login'), reverse('private')))

    # logout

    def test_logout(self):
        self.client.login(username=self.user.username, password=self.password)

        response = self.client.get(reverse('logout'), follow=True)

        self.assertRedirects(response, reverse('login'))
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        self.assertEqual(str(m[0]), login_messages['now_logged_out'])

    def test_logout__while_logged_out(self):
        response = self.client.get(reverse('logout'), follow=True)

        self.assertRedirects(response, "{}?next={}".format(reverse('login'), reverse('logout')))

    # login

    def test_login_get(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'])

    def test_login_post(self):
        data = {'username': self.user.username, 'password': PASSWORD}

        response = self.client.post(reverse('login'), data, follow=True)

        self.assertRedirects(response, reverse('account'))
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)
        self.assertEqual(str(m[0]), login_messages['now_logged_in'])

    # account

    def test_account__logged_in(self):
        self.client.login(username=self.user.username, password=self.password)

        response = self.client.get(reverse('account'))

        self.assertEqual(response.status_code, 200)

    def test_account__logged_out(self):
        response = self.client.get(reverse('account'), follow=True)

        self.assertRedirects(response, "{}?next={}".format(reverse('login'), reverse('account')))

    def test_account__headline_context(self):
        self.client.login(username=self.user.username, password=self.password)

        response = self.client.get(reverse('account'))

        self.assertTrue(response.context['headline_small'])

    def test_account__no_funds_alert(self):
        self.client.login(username=self.user.username, password=self.password)
        subaccount = make_subaccount(self.hotel)
        subaccount.active = False
        subaccount.save()
        self.assertFalse(self.hotel.subaccount.active)

        response = self.client.get(reverse('account'))

        self.assertTrue(response.context['alerts'])
        self.assertIn(
            alert_messages['no_funds_alert'],
            response.content
        )

    def test_account__no_customer_alert(self):
        self.client.login(username=self.user.username, password=self.password)
        self.hotel.customer = None
        self.hotel.save()
        self.assertIsNone(self.hotel.customer)

        response = self.client.get(reverse('account'))

        self.assertTrue(response.context['alerts'])
        self.assertIn(
            alert_messages['no_customer_alert'],
            response.content
        )

    def test_account__no_twilio_phone_number_alert(self):
        self.client.login(username=self.user.username, password=self.password)
        self.hotel.twilio_ph_sid = None
        self.hotel.save()
        self.assertIsNone(self.hotel.twilio_ph_sid)

        response = self.client.get(reverse('account'))

        self.assertTrue(response.context['alerts'])
        self.assertIn(
            alert_messages['no_twilio_phone_number_alert'],
            response.content
        )

    # account - navbar links

    def test_account__login_navbar_links(self):
        self.client.login(username=self.admin.username, password=PASSWORD)

        response = self.client.get(reverse('account'))

        self.assertIn("My Profile", response.content)
        self.assertIn(reverse('main:user_detail', kwargs={'pk': self.admin.pk}), response.content)

        self.assertIn("My Guests", response.content)
        self.assertIn(reverse('concierge:guest_list'), response.content)

        self.assertIn("Logout", response.content)
        self.assertIn(reverse('logout'), response.content)

    # account - side-bar links

    def test_account__side_bar_links__admin(self):
        self.client.login(username=self.admin.username, password=PASSWORD)

        response = self.client.get(reverse('account'))

        # User
        self.assertIn("My Profile", response.content)
        self.assertIn(reverse('main:user_detail', kwargs={'pk': self.admin.pk}), response.content)

        self.assertIn("Change Password", response.content)
        self.assertIn(reverse('password_change'), response.content)

        # Hotel
        self.assertIn("Hotel Info", response.content)
        self.assertIn(reverse('main:hotel_update', kwargs={'pk': self.admin.profile.hotel.pk}), response.content)

        # Guests
        self.assertIn("Guest List", response.content)
        self.assertIn(reverse('concierge:guest_list'), response.content)

        self.assertIn("Add a Guest", response.content)
        self.assertIn(reverse('concierge:guest_create'), response.content)

        # Users
        self.assertIn("Manage Users", response.content)

        self.assertIn("User List", response.content)
        self.assertIn(reverse('main:manage_user_list'), response.content)

        self.assertIn("Add a User", response.content)
        self.assertIn(reverse('main:create_user'), response.content)

        self.assertIn("Add a Manager", response.content)
        self.assertIn(reverse('main:create_manager'), response.content)

        # Auto-Replies
        self.assertIn("Auto Replies", response.content)
        self.assertIn(reverse('concierge:replies'), response.content)

        # PhoneNumbers
        self.assertIn("Phone Numbers List", response.content)
        self.assertIn(reverse('sms:ph_num_list'), response.content)

        self.assertIn("Add a Phone Number", response.content)
        self.assertIn(reverse('sms:ph_num_add'), response.content)

        # Billing
        self.assertIn("Overview", response.content)
        self.assertIn(reverse('payment:summary'), response.content)

        self.assertIn("Account Payment Settings", response.content)
        self.assertIn(reverse('acct_cost_update', kwargs={'pk': self.admin.profile.hotel.pk}), response.content)
        
        self.assertIn("Change / Add Payment Method", response.content)
        self.assertIn(reverse('payment:card_list'), response.content)
        
        self.assertIn("Add Funds", response.content)
        self.assertIn(reverse('payment:one_time_payment'), response.content)
        
        self.assertIn("View Payment History", response.content)
        self.assertIn(reverse('acct_pmt_history'), response.content)

    def test_account__side_bar_links__manager(self):
        self.client.login(username=self.manager.username, password=PASSWORD)

        response = self.client.get(reverse('account'))

        # User
        self.assertIn("My Profile", response.content)
        self.assertIn(reverse('main:user_detail', kwargs={'pk': self.manager.pk}), response.content)

        self.assertIn("Change Password", response.content)
        self.assertIn(reverse('password_change'), response.content)

        # Hotel
        self.assertNotIn("Hotel Info", response.content)
        self.assertNotIn(reverse('main:hotel_update', kwargs={'pk': self.manager.profile.hotel.pk}), response.content)

        # Guests
        self.assertIn("Guest List", response.content)
        self.assertIn(reverse('concierge:guest_list'), response.content)

        self.assertIn("Add a Guest", response.content)
        self.assertIn(reverse('concierge:guest_create'), response.content)

        # Users
        self.assertIn("Manage Users", response.content)

        self.assertIn("User List", response.content)
        self.assertIn(reverse('main:manage_user_list'), response.content)

        self.assertIn("Add a User", response.content)
        self.assertIn(reverse('main:create_user'), response.content)

        self.assertNotIn("Add a Manager", response.content)
        self.assertNotIn(reverse('main:create_manager'), response.content)

        # Auto-Replies
        self.assertIn("Auto Replies", response.content)
        self.assertIn(reverse('concierge:replies'), response.content)

        # PhoneNumbers
        self.assertNotIn("Phone Numbers List", response.content)
        self.assertNotIn(reverse('sms:ph_num_list'), response.content)

        self.assertNotIn("Add a Phone Number", response.content)
        self.assertNotIn(reverse('sms:ph_num_add'), response.content)

        # Billing
        self.assertNotIn("Overview", response.content)
        self.assertNotIn(reverse('payment:summary'), response.content)

        self.assertNotIn("Account Payment Settings", response.content)
        self.assertNotIn(reverse('acct_cost_update', kwargs={'pk': self.manager.profile.hotel.pk}), response.content)
        
        self.assertNotIn("Change / Add Payment Method", response.content)
        self.assertNotIn(reverse('payment:card_list'), response.content)
        
        self.assertNotIn("Add Funds", response.content)
        self.assertNotIn(reverse('payment:one_time_payment'), response.content)
        
        self.assertNotIn("View Payment History", response.content)
        self.assertNotIn(reverse('acct_pmt_history'), response.content)

    def test_account__side_bar_links__user(self):
        self.client.login(username=self.user.username, password=PASSWORD)

        response = self.client.get(reverse('account'))

        # User
        self.assertIn("My Profile", response.content)
        self.assertIn(reverse('main:user_detail', kwargs={'pk': self.user.pk}), response.content)

        self.assertIn("Change Password", response.content)
        self.assertIn(reverse('password_change'), response.content)

        # Hotel
        self.assertNotIn("Hotel Info", response.content)
        self.assertNotIn(reverse('main:hotel_update', kwargs={'pk': self.user.profile.hotel.pk}), response.content)

        # Guests
        self.assertIn("Guest List", response.content)
        self.assertIn(reverse('concierge:guest_list'), response.content)

        self.assertIn("Add a Guest", response.content)
        self.assertIn(reverse('concierge:guest_create'), response.content)

        # Users
        self.assertNotIn("Manage Users", response.content)

        self.assertNotIn("User List", response.content)
        self.assertNotIn(reverse('main:manage_user_list'), response.content)

        self.assertNotIn("Add a User", response.content)
        self.assertNotIn(reverse('main:create_user'), response.content)

        self.assertNotIn("Add a Manager", response.content)
        self.assertNotIn(reverse('main:create_manager'), response.content)

        # Auto-Replies
        self.assertNotIn("Auto Replies", response.content)
        self.assertNotIn(reverse('concierge:replies'), response.content)

        # PhoneNumbers
        self.assertNotIn("Phone Numbers List", response.content)
        self.assertNotIn(reverse('sms:ph_num_list'), response.content)

        self.assertNotIn("Add a Phone Number", response.content)
        self.assertNotIn(reverse('sms:ph_num_add'), response.content)

        # Billing
        self.assertNotIn("Overview", response.content)
        self.assertNotIn(reverse('payment:summary'), response.content)

        self.assertNotIn("Account Payment Settings", response.content)
        self.assertNotIn(reverse('acct_cost_update', kwargs={'pk': self.user.profile.hotel.pk}), response.content)
        
        self.assertNotIn("Change / Add Payment Method", response.content)
        self.assertNotIn(reverse('payment:card_list'), response.content)
        
        self.assertNotIn("Add Funds", response.content)
        self.assertNotIn(reverse('payment:one_time_payment'), response.content)
        
        self.assertNotIn("View Payment History", response.content)
        self.assertNotIn(reverse('acct_pmt_history'), response.content)

    ### inherit from - django.contrib.auth.forms

    ### 2 views for password change

    def test_password_change(self):
        # login required view
        response = self.client.get(reverse('password_change'))
        self.assertEqual(response.status_code, 302)

        # login
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('password_change'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'])

    def test_password_change_done(self):
        self.client.login(username=self.user.username, password=self.password)

        response = self.client.get(reverse('password_change_done'))

        self.assertEqual(response.status_code, 200)

    def test_password_change_done__logged_out(self):
        # login required view
        response = self.client.get(reverse('password_change_done'), follow=True)
        
        self.assertRedirects(response, "{}?next={}".format(reverse('login'),
            reverse('password_change_done')))

    ### 4 views for password reset

    def test_password_reset(self):
        response = self.client.get(reverse('password_reset'))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'])
        self.assertTrue(response.context['headline'])

    def test_password_reset_done(self):
        response = self.client.get(reverse('password_reset_done'))

        self.assertEqual(response.status_code, 200)

    def test_password_reset_confirm(self):
        # TODO: write an integration for Form test for this
        pass

    def test_password_reset_complete(self):
        response = self.client.get(reverse('password_reset_complete'))

        self.assertEqual(response.status_code, 200)


class RegistrationTests(TestCase):

    def setUp(self):
        create._get_groups_and_perms()
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel, group="hotel_admin")
        # Login
        self.client.login(username=self.user.username, password=PASSWORD)

    # register_step3

    def test_get(self):
        response = self.client.get(reverse('register_step3'))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], AcctCostForm)

    def test_get__logged_out(self):
        self.client.logout()

        response = self.client.get(reverse('register_step3'), follow=True)

        self.assertRedirects(response, "{}?next={}".format(reverse('login'), reverse('register_step3')))

    def test_create(self):
        # Step 3
        response = self.client.post(reverse('register_step3'),
            CREATE_ACCTCOST_DICT, follow=True)
        self.assertRedirects(response, reverse('payment:register_step4'))
        # created n linked to Hotel
        acct_cost = AcctCost.objects.get(hotel=self.hotel)
        self.assertIsInstance(acct_cost, AcctCost)

        # Dave tries to view the page again and is redirected to the UpdateView
        response = self.client.get(reverse('register_step3'), follow=True)
        self.assertRedirects(response, reverse('register_step3_update', kwargs={'pk': acct_cost.pk}))

    def test_update(self):
        # Step 3 UpdateView
        # Dave wants to update his choice
        acct_cost = mommy.make(AcctCost, hotel=self.hotel)
        response = self.client.get(reverse('register_step3_update', kwargs={'pk': acct_cost.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], AcctCostForm)

    def test_update__logged_out(self):
        # Step 3 UpdateView
        # Dave wants to update his choice
        self.client.logout()
        acct_cost = mommy.make(AcctCost, hotel=self.hotel)

        response = self.client.get(reverse('register_step3_update', kwargs={'pk': acct_cost.pk}),
            follow=True)

        self.assertRedirects(response, "{}?next={}".format(reverse('login'), reverse('register_step3')))

    def test_update__no_account_cost(self):
        # Dave doesn't have an AcctCost yet, and tries to go to another Hotel's AcctCost page
        other_hotel = create_hotel()
        other_acct_cost = mommy.make(AcctCost, hotel=other_hotel)
        response = self.client.get(reverse('register_step3_update',
            kwargs={'pk': other_acct_cost.pk}), follow=True)
        self.assertRedirects(response, reverse('register_step3'))

    def test_update__other_hotel_account_cost(self):
        # Dave has an AcctCost, and tries to go to another Hotel's AcctCost page
        acct_cost = mommy.make(AcctCost, hotel=self.hotel)
        other_hotel = create_hotel()
        other_acct_cost = mommy.make(AcctCost, hotel=other_hotel)
        response = self.client.get(reverse('register_step3_update',
            kwargs={'pk': other_acct_cost.pk}), follow=True)
        self.assertRedirects(response, reverse('register_step3_update',
            kwargs={'pk': acct_cost.pk}))


class AcctStmtAndOtherAccountViewTests(TestCase):

    fixtures = ['trans_type.json']

    def setUp(self):
        self.hotel = create_hotel()
        create._get_groups_and_perms()
        self.admin = create_hotel_user(hotel=self.hotel, username='admin', group='hotel_admin')
        # dates
        self.today = datetime.datetime.today()
        self.year = self.today.year
        self.month = self.today.month
        # Account Data
        self.pricing = mommy.make(Pricing, hotel=self.hotel)
        self.acct_trans = create_acct_trans(hotel=self.hotel)
        self.acct_stmt = AcctStmt.objects.get_or_create(hotel=self.hotel, year=self.year, month=self.month)
        # Login
        self.client.login(username=self.admin.username, password=PASSWORD)

        # Create other Hotel to show that the 1st main Hotel is not affected
        # and all views / queries return the expected results
        self.hotel_2 = create_hotel()
        self.acct_stmt = create_acct_stmt(hotel=self.hotel_2, year=self.year, month=self.month)
        self.acct_trans = create_acct_trans(hotel=self.hotel_2)

    def tearDown(self):
        self.client.logout()

    ### ACCT COST

    def test_acct_cost_update__get(self):
        acct_cost, created = AcctCost.objects.get_or_create(self.hotel)

        response = self.client.get(reverse('acct_cost_update', kwargs={'pk':acct_cost.pk}))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'])
        self.assertTrue(response.context['breadcrumbs'])

    def test_acct_cost_update__get__logged_out(self):
        self.client.logout()
        acct_cost, created = AcctCost.objects.get_or_create(self.hotel)

        response = self.client.get(reverse('acct_cost_update', kwargs={'pk':acct_cost.pk}),
            follow=True)

        self.assertRedirects(response, "{}?next={}".format(reverse('login'),
            reverse('acct_cost_update', kwargs={'pk':acct_cost.pk})))

    def test_acct_cost_update_post(self):
        data = {
            'balance_min': BALANCE_AMOUNTS[0][0],
            'recharge_amt': CHARGE_AMOUNTS[0][0],
            'auto_recharge': True
        }
        acct_cost, created = AcctCost.objects.get_or_create(self.hotel)

        response = self.client.post(reverse('acct_cost_update', kwargs={'pk':acct_cost.pk}),
            data, follow=True)

        self.assertRedirects(response, reverse('payment:summary'))
        # success message from ``FormUpdateMessageMixin``
        m = list(response.context['messages'])
        self.assertEqual(len(m), 1)

    ### ACCT STMT DETAIL

    def test_acct_stmt_detail__response(self):
        response = self.client.get(reverse('acct_stmt_detail',
            kwargs={'year': self.year, 'month': self.month}))

        self.assertEqual(response.status_code, 200)

    def test_acct_stmt_detail__logged_out(self):
        self.client.logout()

        response = self.client.get(reverse('acct_stmt_detail',
            kwargs={'year': self.year, 'month': self.month}), follow=True)

        self.assertRedirects(response, "{}?next={}".format(reverse('login'),
            reverse('acct_stmt_detail', kwargs={'year': self.year, 'month': self.month})))

    def test_acct_stmt_detail__context(self):
        response = self.client.get(reverse('acct_stmt_detail',
            kwargs={'year': self.year, 'month': self.month}))

        self.assertTrue(response.context['acct_stmt'])
        self.assertTrue(response.context['acct_stmts'])
        for ea in ['sms_used', 'phone_number']:
            self.assertIn(ea, response.context['debit_trans_types'])

    def test_acct_stmt_detail_breadcrumbs(self):
        response = self.client.get(reverse('acct_stmt_detail',
            kwargs={'year': self.year, 'month': self.month}))

        self.assertTrue(response.context['breadcrumbs'])

    def test_context_acct_trans(self):
        acct_tran = AcctTrans.objects.filter(hotel=self.hotel, trans_type__name='sms_used').first()
        self.assertTrue(acct_tran)

        response = self.client.get(reverse('acct_stmt_detail',
            kwargs={'year': self.year, 'month': self.month}))

        self.assertTrue(response.context['monthly_trans'])
        # the "sms_used" AcctTrans is populating the table how we expect
        self.assertIn(acct_tran.insert_date.strftime("%B %-d, %Y"), response.content)
        self.assertIn("sms used", response.content)
        self.assertIn(str(acct_tran.sms_used), response.content)
        self.assertIn('${:.2f}'.format(acct_tran.amount/100.0), response.content)
        self.assertIn('${:.2f}'.format(acct_tran.balance/100.0), response.content)

    ### ACCT PMT HISTORY

    def test_acct_pmt_history__response(self):
        response = self.client.get(reverse('acct_pmt_history'))

        self.assertEqual(response.status_code, 200)

    def test_acct_pmt_history__logged_out(self):
        self.client.logout()

        response = self.client.get(reverse('acct_pmt_history'), follow=True)

        self.assertRedirects(response, "{}?next={}".format(reverse('login'),
            reverse('acct_pmt_history')))

    def test_acct_pmt_history__context(self):
        response = self.client.get(reverse('acct_pmt_history'))

        self.assertTrue(response.context['object_list'])

    def test_acct_pmt_history__breadcrumbs(self):
        response = self.client.get(reverse('acct_pmt_history'))

        self.assertTrue(response.context['breadcrumbs'])

    def test_acct_pmt_history__context_record(self):
        acct_tran = AcctTrans.objects.filter(hotel=self.hotel, trans_type__name='init_amt').first()
        self.assertTrue(acct_tran)

        response = self.client.get(reverse('acct_pmt_history'))

        self.assertIn(acct_tran.insert_date.strftime("%B %-d, %Y"), response.content)
        self.assertIn("init amt", response.content)
        self.assertIn('${:.2f}'.format(acct_tran.amount/100.0), response.content)


class APITests(TestCase):

    def setUp(self):
        self.hotel = create_hotel()
        self.pricing = mommy.make(Pricing, hotel=self.hotel)

    def test_pricing(self):
        response = self.client.get(reverse('api_pricing'))
        self.assertEqual(response.status_code, 200)

    def test_pricing_get_indiv(self):
        price = Pricing.objects.first()
        response = self.client.get(reverse('api_pricing', kwargs={'pk': price.pk}))
        self.assertEqual(response.status_code, 200)


class AccountDeactivatedTests(TestCase):
    # Test Rending of view, template path is correct, url
    # User of each permission type needed

    def setUp(self):
        create._get_groups_and_perms()
        self.password = PASSWORD

        self.hotel = create_hotel()
        self.admin = create_hotel_user(self.hotel, 'admin', 'hotel_admin')
        self.manager = create_hotel_user(self.hotel, 'manager', 'hotel_manager')
        self.user = create_hotel_user(self.hotel, 'user')
        # Subaccount
        self.sub = make_subaccount_live(self.hotel)
        # Login
        self.client.login(username=self.user.username, password=self.password)

    def tearDown(self):
        # set back to "active" b/c this is a live Twilio Subaccount
        self.assertEqual(self.sub.activate(), 'active')

    # subaccount - warnings

    def test_active_subaccount_no_warning_message(self):
        self.assertTrue(self.hotel.subaccount.active)

        response = self.client.get(reverse('account'))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            "SMS sending and receiving has been deactivated",
            response.content
        )

    def test_deactivated_subaccount_shows_warning_message(self):
        self.sub.deactivate()

        response = self.client.get(reverse('account'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "SMS sending and receiving has been deactivated",
            response.content
        )

    # not stripe customer - warnings

    def test_no_stripe_customer_warning(self):
        self.assertIsNone(self.hotel.customer)

        response = self.client.get(reverse('account'))

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "No account funds. Click the link to add initial funds and avoid the account being deactivated.",
            response.content
        )

    def test_no_stripe_customer_warning__not_present(self):
        customer = mommy.make(Customer)
        self.hotel = self.hotel.update_customer(customer)
        self.assertIsNotNone(self.hotel.customer)

        response = self.client.get(reverse('account'))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn(
            "No account funds. Click the link to add initial funds and avoid the account being deactivated.",
            response.content
        )


class LoginTests(TestCase):

    def setUp(self):
        self.password = '1111'
        self.user = User.objects.create_user('Bobby',
            settings.DEFAULT_FROM_EMAIL, self.password)

    def test_get(self):
        response = self.client.get(reverse('login'))
        assert response.status_code == 200
        assert response.context['form']  


class PasswordChangeTests(TestCase):

    def setUp(self):
        self.password = '1111'
        self.new_password = '2222'
        self.user = User.objects.create_user('Bobby',
            settings.DEFAULT_FROM_EMAIL, self.password)

    def test_get(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('password_change'))
        assert response.status_code == 200
        assert response.context['form']

    def test_get_done(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('password_change_done'))
        assert response.status_code == 200


class PasswordResetTests(TestCase):

    def setUp(self):
        self.password = '1111'
        self.new_password = '2222'
        self.user = User.objects.create_user('Bobby',
            settings.DEFAULT_FROM_EMAIL, self.password)

    def test_get(self):
        response = self.client.get(reverse('password_reset'))
        assert response.status_code == 200
        assert response.context['form']

    def test_get_done(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('password_reset_done'))
        assert response.status_code == 200

    def test_get_done(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('password_reset_complete'))
        assert response.status_code == 200
