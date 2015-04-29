from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework.urlpatterns import format_suffix_patterns

from textress.views import (handler404, handler500, TermsView)
from concierge import views
from account.views import PricingListAPIView, PricingRetrieveAPIView


admin.autodiscover()

api_urlpatterns = [
    url(r'^messages/$', views.MessageListCreateAPIView.as_view(), name='api_messages'),
    url(r'^messages/(?P<pk>\d+)/$', views.MessageRetrieveAPIView.as_view(), name='api_messages'),

    url(r'^guest-messages/$', views.GuestMessageListAPIView.as_view(), name='api_guest_messages'),
    url(r'^guest-messages/(?P<pk>\d+)/$', views.GuestMessageRetrieveAPIView.as_view(), name='api_guest_messages'),

    url(r'^guests/$', views.GuestListCreateAPIView.as_view(), name='api_guests'),
    url(r'^guests/(?P<pk>\d+)/$', views.GuestRetrieveUpdateAPIView.as_view(), name='api_guests'),

    url(r'^users/$', views.UserListCreateAPIView.as_view(), name='api_users'),
    url(r'^users/(?P<pk>\d+)/$', views.UserRetrieveUpdateAPIView.as_view(), name='api_users'),

    url(r'^account/pricing/$', PricingListAPIView.as_view(), name='pricing'),
    url(r'^account/pricing/(?P<pk>\d+)/$', PricingRetrieveAPIView.as_view(), name='pricing'),

    # Receive Twilio Config'd URI
    url(r'^receive/sms_url/$', views.ReceiveSMSView.as_view(), name='receive_sms'),
    ]


urlpatterns = format_suffix_patterns(api_urlpatterns)


urlpatterns += patterns('',
    # Admin
    url(r'^aronysidoro/', include(admin.site.urls)),
    # Apps
    url(r'account/', include('account.urls')),
    url(r'concierge/', include('concierge.urls', namespace='concierge')),
    url(r'', include('contact.urls', namespace='contact')),
    url(r'', include('main.urls', namespace='main')),
    url(r'payment/', include('payment.urls', namespace='payment')),
    url(r'sms/', include('sms.urls', namespace='sms')),
    # django-rest-framework
    url(r'api/', include(api_urlpatterns)),
    url(r'api/v1/auth/login/', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # Pages
    url(r'^404/$', handler404),
    url(r'^500/$', handler500),
    url(r'^info/terms-and-conditions/$', TermsView.as_view(), name='terms'),
)
