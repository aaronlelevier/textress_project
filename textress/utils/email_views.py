from django.conf import settings
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView

from main.models import UserProfile
from payment.models import Charge


class EmailIndexView(TemplateView):

    template_name = "email/index.html"


class AccountChargedView(TemplateView):

    template_name = "email/account_charged/email.html"

    def get_context_data(self, **kwargs):
        context = super(AccountChargedView, self).get_context_data(**kwargs)
        context['user'] = User.objects.first()
        context['charge'] = Charge.objects.first()
        context['textess_contact_email'] = settings.DEFAULT_EMAIL_BILLING
        context['textress_phone'] = settings.TEXTRESS_PHONE_NUMBER
        context['SITE_URL'] = settings.SITE_URL
        return context


class AutoRechargeFailedView(TemplateView):

    template_name = "email/auto_recharge_failed/email.html"

    def get_context_data(self, **kwargs):
        context = super(AutoRechargeFailedView, self).get_context_data(**kwargs)
        user_profile = UserProfile.objects.exclude(hotel__isnull=True)[0]
        context['user'] = user_profile.user
        context['hotel'] = user_profile.hotel
        context['textess_contact_email'] = settings.DEFAULT_EMAIL_SUPPORT
        context['textress_phone'] = settings.TEXTRESS_PHONE_NUMBER
        context['SITE_URL'] = settings.SITE_URL
        return context
