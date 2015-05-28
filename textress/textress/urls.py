from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework.urlpatterns import format_suffix_patterns

from textress import views


admin.autodiscover()

urlpatterns = patterns('',
    # Admin
    url(r'^aronysidoro/', include(admin.site.urls)),
    # Apps
    url(r'', include('account.urls')),
    # url(r'', include('concierge.urls', namespace='concierge')),
    url(r'', include('main.urls', namespace='main')),
    url(r'', include('payment.urls', namespace='payment')),
    # url(r'', include('sms.urls', namespace='sms')),
    
    # url(r'api/v1/auth/login/', 'rest_framework_jwt.views.obtain_jwt_token'),
    # url(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),

    # Textress Views
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^terms-and-conditions/$', views.TermsNCondView.as_view(), name='terms_n_cond'),
    url(r'^404/$', views.handler404, name='404'),
    url(r'^500/$', views.handler500, name='500'),
)
