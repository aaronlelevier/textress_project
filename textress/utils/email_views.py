from django.conf import settings
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView

from main.models import UserProfile
from payment.models import Charge
from sms.models import PhoneNumber


class EmailViewContextMixin(object):

    def get_context_data(self, **kwargs):
        context = super(EmailViewContextMixin, self).get_context_data(**kwargs)
        context['textess_contact_email'] = settings.DEFAULT_EMAIL_BILLING
        context['textress_phone'] = settings.TEXTRESS_PHONE_NUMBER
        context['SITE_URL'] = settings.SITE_URL
        return context


class EmailIndexView(TemplateView):

    template_name = "email/index.html"


class AccountChargedView(EmailViewContextMixin, TemplateView):

    template_name = "email/account_charged/email.html"

    def get_context_data(self, **kwargs):
        context = super(AccountChargedView, self).get_context_data(**kwargs)
        context['user'] = User.objects.first()
        context['charge'] = Charge.objects.first()
        return context


class AutoRechargeFailedView(EmailViewContextMixin, TemplateView):

    template_name = "email/auto_recharge_failed/email.html"

    def get_context_data(self, **kwargs):
        context = super(AutoRechargeFailedView, self).get_context_data(**kwargs)
        user_profile = UserProfile.objects.exclude(hotel__isnull=True)[0]
        context['user'] = user_profile.user
        context['hotel'] = user_profile.hotel
        return context


class ChargeFailedView(EmailViewContextMixin, TemplateView):

    template_name = "email/charge_failed/email.html"

    def get_context_data(self, **kwargs):
        context = super(ChargeFailedView, self).get_context_data(**kwargs)
        context['user'] = User.objects.first()
        context['amount'] = Charge.objects.first().amount
        return context

class SendDeleteUnknownNumberFailed(EmailViewContextMixin, TemplateView):

    template_name = "email/delete_unknown_number_failed/email.html"

    def get_context_data(self, **kwargs):
        context = super(SendDeleteUnknownNumberFailed, self).get_context_data(**kwargs)
        context['ph_num'] = PhoneNumber.objects.first()
        return context
