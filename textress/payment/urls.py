from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from payment import views
from utils.decorators import required, logout_required


register_patterns = patterns('',
    url(r'^step4/$', views.RegisterPmtView.as_view(), name='register_step4'),
    url(r'^success/$', views.RegisterSuccessView.as_view(), name='register_success'),
)

payment_patterns = patterns('',
    url(r'^$', views.SummaryView.as_view(), name='summary'),
    url(r'^manage-payment-methods/$', views.CardListView.as_view(), name='card_list'),
    url(r'^set-default-card(?P<pk>\w+)/$', views.set_default_card_view, name='set_default_card'),
    url(r'^delete-card/(?P<pk>\w+)/$', views.delete_card_view, name='delete_card'),
    # Stripe
    url(r'^one-time-payment/$', views.OneTimePaymentView.as_view(), name='one_time_payment'),
)

urlpatterns = patterns('',
    # Registration
    url(r'^register/', include(register_patterns)),
    url(r'^billing/', include(payment_patterns)),
)
