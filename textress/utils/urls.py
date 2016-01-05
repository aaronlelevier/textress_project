from django.conf.urls import patterns, include, url

from utils import email_views


urlpatterns = patterns('',
    url(r'^$', email_views.EmailIndexView.as_view(), name='index'),
    url(r'^account_charged/$', email_views.AccountChargedView.as_view(), name='account_charged'),
    url(r'^auto_recharge_failed/$', email_views.AutoRechargeFailedView.as_view(), name='auto_recharge_failed'),
    url(r'^charge_failed/$', email_views.ChargeFailedView.as_view(), name='charge_failed'),
    url(r'^send_delete_unknown_number_failed_email/$', email_views.SendDeleteUnknownNumberFailed.as_view(),
        name='send_delete_unknown_number_failed_email'),
)
