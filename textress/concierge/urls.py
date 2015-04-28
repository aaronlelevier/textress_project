from django.conf.urls import patterns, include, url

from rest_framework.urlpatterns import format_suffix_patterns

from concierge import views


guest_patterns = patterns('',
    url(r'^$', views.GuestListView.as_view(), name='guest_list'),
    url(r'^detail/(?P<pk>\d+)/$', views.GuestDetailView.as_view(), name='guest_detail'),
    url(r'^create/$', views.GuestCreateView.as_view(), name='guest_create'),
    url(r'^update/(?P<pk>\d+)/$', views.GuestUpdateView.as_view(), name='guest_update'),
    url(r'^delete/(?P<pk>\d+)/$', views.GuestDeleteView.as_view(), name='guest_delete'),
    )

message_patterns = patterns('',
    url(r'^detail/(?P<pk>\d+)/$', views.MessageDetailView.as_view(), name='message_detail'),
    url(r'^guest/(?P<pk>\d+)/$', views.MessageListView.as_view(), name='message_list'),
    )

urlpatterns = patterns('',
    url(r'^guests/', include(guest_patterns)),
    url(r'^message/', include(message_patterns)),
    )