from django.conf.urls import patterns, include, url

from payment import views


register_patterns = patterns('',
    url(r'^step4/$', views.RegisterPmtView.as_view(), name='register_step4'),
    url(r'^success/$', views.RegisterSuccessView.as_view(), name='register_success'),
    )

payment_patterns = patterns('',
    url(r'^$', views.SummaryView.as_view(), name='summary'),
    url(r'^create/$', views.CardCreateView.as_view(), name='card_create'),
    url(r'^detail/(?P<pk>\w+)/$', views.CardDetailView.as_view(), name='card_detail'),
    url(r'^update/(?P<pk>\w+)/$', views.CardUpdateView.as_view(), name='card_update'),
    url(r'^remove/(?P<pk>\w+)/$', views.CardDeleteView.as_view(), name='card_delete'),
    )

urlpatterns = patterns('',
    # Registration
    url(r'^register/', include(register_patterns)),
    url(r'^billing/', include(payment_patterns)),
    )