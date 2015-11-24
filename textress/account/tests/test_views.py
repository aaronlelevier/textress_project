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
    CREATE_USER_DICT, CREATE_HOTEL_DICT, PASSWORD)
from utils import create


class AcctStmtViewTests(TestCase):

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
        self.acct_stmt = create_acct_stmt(hotel=self.hotel, year=self.year, month=self.month)
        self.acct_trans = create_acct_trans(hotel=self.hotel)
        # Login
        self.client.login(username=self.admin.username, password=PASSWORD)

        # Create other Hotel to show that the 1st main Hotel is not affected
        # and all views / queries return the expected results
        self.hotel_2 = create_hotel()
        self.acct_stmt = create_acct_stmt(hotel=self.hotel_2, year=self.year, month=self.month)
        self.acct_trans = create_acct_trans(hotel=self.hotel_2)

    def tearDown(self):
        self.client.logout()

    ### ACCT STMT DETAIL

    def test_acct_stmt_detail_response(self):
        response = self.client.get(reverse('acct_stmt_detail',
            kwargs={'year': self.year, 'month': self.month}))
        self.assertEqual(response.status_code, 200)

    def test_acct_stmt_detail_context(self):
        response = self.client.get(reverse('acct_stmt_detail',
            kwargs={'year': self.year, 'month': self.month}))
        self.assertTrue(response.context['acct_stmt'])
        self.assertTrue(response.context['acct_stmts'])

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
        self.assertIn(acct_tran.insert_date.strftime("%b. %d, %Y"), response.content)
        self.assertIn("sms used", response.content)
        self.assertIn(str(acct_tran.sms_used), response.content)
        self.assertIn('${:.2f}'.format(acct_tran.amount/100.0), response.content)
        self.assertIn('${:.2f}'.format(acct_tran.balance/100.0), response.content)

    ### ACCT PMT HISTORY

    def test_acct_pmt_history_response(self):
        response = self.client.get(reverse('acct_pmt_history'))
        self.assertEqual(response.status_code, 200)

    def test_acct_pmt_history_context(self):
        response = self.client.get(reverse('acct_pmt_history'))
        self.assertTrue(response.context['object_list'])

    def test_acct_pmt_history_breadcrumbs(self):
        response = self.client.get(reverse('acct_pmt_history'))
        self.assertTrue(response.context['breadcrumbs'])

    def test_acct_pmt_history_context(self):
        acct_tran = AcctTrans.objects.filter(hotel=self.hotel, trans_type__name='init_amt').first()
        self.assertTrue(acct_tran)

        response = self.client.get(reverse('acct_pmt_history'))

        self.assertIn(acct_tran.insert_date.strftime("%b. %d, %Y"), response.content)
        self.assertIn("init amt", response.content)
        self.assertIn('${:.2f}'.format(acct_tran.amount/100.0), response.content)
        
    ### ACCT COST

    def test_acct_cost_update_get(self):
        acct_cost, created = AcctCost.objects.get_or_create(self.hotel)
        response = self.client.get(reverse('acct_cost_update', kwargs={'pk':acct_cost.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'])
        self.assertTrue(response.context['breadcrumbs'])

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

    def test_update_no_account_cost(self):
        # Dave doesn't have an AcctCost yet, and tries to go to another Hotel's AcctCost page
        other_hotel = create_hotel()
        other_acct_cost = mommy.make(AcctCost, hotel=other_hotel)
        response = self.client.get(reverse('register_step3_update',
            kwargs={'pk': other_acct_cost.pk}), follow=True)
        self.assertRedirects(response, reverse('register_step3'))

    def test_update_other_hotel_account_cost(self):
        # Dave has an AcctCost, and tries to go to another Hotel's AcctCost page
        acct_cost = mommy.make(AcctCost, hotel=self.hotel)
        other_hotel = create_hotel()
        other_acct_cost = mommy.make(AcctCost, hotel=other_hotel)
        response = self.client.get(reverse('register_step3_update',
            kwargs={'pk': other_acct_cost.pk}), follow=True)
        self.assertRedirects(response, reverse('register_step3_update',
            kwargs={'pk': acct_cost.pk}))


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

    ### inherit from - django.contrib.auth.forms

    def test_account_logged_in(self):
        # Dave as a logged in User can access his account (profile) view
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('account'))
        self.assertEqual(response.status_code, 200)

    def test_account_logged_out(self):
        # logged out Dave cannot access it
        response = self.client.get(reverse('account'))
        self.assertEqual(response.status_code, 302)

    def test_headline_context(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('account'))
        self.assertTrue(response.context['headline_small'])

    def test_login(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'])

    ### 2 views for password change

    def test_password_change(self):
        # login required view
        response = self.client.get(reverse('password_change'))
        self.assertEqual(response.status_code, 302)

        # login
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('password_change'))
        self.assertEqual(response.status_code, 200)
        assert response.context['form']

    def test_password_change_done(self):
        # login required view
        response = self.client.get(reverse('password_change_done'))
        self.assertEqual(response.status_code, 302)

        # login
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('password_change_done'))
        self.assertEqual(response.status_code, 200)

    ### 4 views for password reset

    def test_password_reset(self):
        response = self.client.get(reverse('password_reset'))
        self.assertEqual(response.status_code, 200)
        assert response.context['form']
        assert response.context['headline']

    def test_password_reset_done(self):
        response = self.client.get(reverse('password_reset_done'))
        self.assertEqual(response.status_code, 200)

    def test_password_reset_confirm(self):
        # TODO: write an integration for Form test for this
        pass

    def test_password_reset_complete(self):
        response = self.client.get(reverse('password_reset_complete'))
        self.assertEqual(response.status_code, 200)

    def test_alert_phone_number(self):
        self.client.login(username=self.user.username, password=self.password)
        self.assertIsNone(self.hotel.twilio_ph_sid)
        response = self.client.get(reverse('account'))
        self.assertTrue(response.context['alerts'])
        # No alert if ``hotel.twilio_ph_sid``
        self.hotel.twilio_ph_sid = 'some value'
        self.hotel.save()
        self.assertTrue(self.hotel.twilio_ph_sid)
        response = self.client.get(reverse('account'))
        with self.assertRaises(KeyError):
            response.context['alerts']


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


class RoutingViewTests(TestCase):

    def setUp(self):
        self.password = PASSWORD
        self.hotel = create_hotel()
        self.user = create_hotel_user(self.hotel)

    def test_private(self):
        # Not logged in get()
        response = self.client.get(reverse('private'))
        assert response.status_code == 302

        # Logged in
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('private'), follow=True)
        self.assertRedirects(response, reverse('account'))

    def test_login_error(self):
        response = self.client.get(reverse('login_error'), follow=True)
        self.assertRedirects(response, reverse('login'))

    def test_logout(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('logout'), follow=True)
        self.assertRedirects(response, reverse('login'))

    def test_verify_logout(self):
        self.client.login(username=self.user.username, password=self.password)
        response = self.client.get(reverse('verify_logout'))
        assert response.status_code == 200
        