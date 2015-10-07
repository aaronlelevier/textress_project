from django.conf.urls import patterns, include, url

from concierge import views


api_patterns = patterns('',
    url(r'^messages/$', views.MessageListCreateAPIView.as_view(), name='api_messages'),
    url(r'^messages/(?P<pk>\d+)/$', views.MessageRetrieveAPIView.as_view(), name='api_messages'),

    url(r'^guest-messages/$', views.GuestMessageListAPIView.as_view(), name='api_guest_messages'),
    url(r'^guest-messages/(?P<pk>\d+)/$', views.GuestMessageRetrieveAPIView.as_view(), name='api_guest_messages'),

    url(r'^guests/$', views.GuestListCreateAPIView.as_view(), name='api_guests'),
    url(r'^guests/(?P<pk>\d+)/$', views.GuestRetrieveUpdateAPIView.as_view(), name='api_guests'),

    # url(r'^replies/$', views.ReplyAPIView, name='api_replies'),
    # url(r'^replies/(?P<pk>\d+)/$', views.ReplyAPIView, name='api_replies'),

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
    url(r'^auto-replies/$', views.ReplyView.as_view(), name='replies'),

    )