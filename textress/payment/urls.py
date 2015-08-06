from django.conf.urls import patterns, include, url

from payment import views


register_patterns = patterns('',
    url(r'^step4/$', views.RegisterPmtView.as_view(), name='register_step4'),
    url(r'^success/$', views.RegisterSuccessView.as_view(), name='register_success'),
    )

payment_patterns = patterns('',
    url(r'^$', views.SummaryView.as_view(), name='summary'),
    url(r'^manage-payment-methods/$', views.CardListView.as_view(), name='card_list'),
    url(r'^update-default-card/(?P<pk>\w+)/$', views.CardUpdateDefaultView.as_view(), name='card_update_default'),
    url(r'^remove/(?P<pk>\w+)/$', views.CardDeleteView.as_view(), name='card_delete'),
    # Stripe
    # url(r'^one-time-payment/$', views.OneTimePaymentView.as_view(), name='one_time_payment'),
    )

urlpatterns = patterns('',
    # Registration
    url(r'^register/', include(register_patterns)),
    url(r'^billing/', include(payment_patterns)),
    )