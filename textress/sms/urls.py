from django.conf.urls import patterns, include, url

from sms import views


urlpatterns = patterns('',
    # Business
    url(r'^try-it-out/$', views.DemoView.as_view(), name='demo'),

)