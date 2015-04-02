from django.conf.urls import patterns, include, url
from django.contrib import admin

from textress.views import handler404, handler500


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'textress.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^aronysidoro/', include(admin.site.urls)),
    url(r'^404/$', handler404, name="404"),
    url(r'^500/$', handler500, name="500"),

    # APP URLS
    url(r'', include('contact.urls', namespace='contact')),
)
