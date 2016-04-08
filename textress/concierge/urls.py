from django.conf.urls import patterns, include, url

from concierge import views


api_patterns = patterns('',
    # Receive Twilio Config'd URI
    url(r'^receive/sms_url/$', views.ReceiveSMSView.as_view(), name='receive_sms'),
    )

guest_patterns = patterns('',
    url(r'^$', views.GuestListView.as_view(), name='guest_list'),
    url(r'^detail/(?P<pk>\d+)/$', views.GuestDetailView.as_view(), name='guest_detail'),
    url(r'^create/$', views.GuestCreateView.as_view(), name='guest_create'),
    url(r'^update/(?P<pk>\d+)/$', views.GuestUpdateView.as_view(), name='guest_update'),
    url(r'^delete/(?P<pk>\d+)/$', views.GuestDeleteView.as_view(), name='guest_delete'),
    )

urlpatterns = patterns('',
    url(r'^api/', include(api_patterns)),
    url(r'^guests/', include(guest_patterns)),
    # No Prefix
    url(r'^send-welcome/$', views.SendWelcomeView.as_view(), name='send_welcome'),
    url(r'^auto-replies/$', views.ReplyView.as_view(), name='replies'),
    )