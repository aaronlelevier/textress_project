from django.conf.urls import patterns, url, include

from contact import views


### NOT IN USE ###

# api_patterns = patterns('',
#     # # REST
#     url(r'^contact/$', views.ContactListCreateAPIView.as_view(), name='api_contact'),
#     url(r'^faq/$', views.FAQListAPIView.as_view(), name='api_contact'),
#     url(r'^faq/(?P<pk>\d+)/$', views.FAQRetrieveAPIView.as_view(), name='api_contact'),
#     )

# urlpatterns = patterns('',
#     url(r'^api/', include(api_patterns)),
#     )