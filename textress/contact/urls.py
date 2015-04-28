from django.conf.urls import patterns, url

from contact import views


urlpatterns = patterns('',
    url(r'^$', views.ComingSoonView.as_view(), name='coming_soon'),

    # # REST
    url(r'^api/contact/$', views.ContactListCreateAPIView.as_view(), name='api_contact'),
    )