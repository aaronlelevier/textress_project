from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin

from rest_framework import routers

from concierge import views_api as concierge_views
from concierge.views_api import CurrentUserAPIView
from textress import views


admin.autodiscover()

router = routers.DefaultRouter()

# API
router.register(r'guests', concierge_views.GuestAPIView)
router.register(r'guest-messages', concierge_views.GuestMessagesAPIView)
router.register(r'messages', concierge_views.MessageAPIView)
router.register(r'reply', concierge_views.ReplyAPIView)
router.register(r'trigger', concierge_views.TriggerAPIView)
router.register(r'trigger-type', concierge_views.TriggerTypeAPIView)

urlpatterns = patterns('',
    # Admin
    url(r'^aronysidoro/', include(admin.site.urls)),
    # Apps
    url(r'', include('account.urls')),
    url(r'', include('concierge.urls', namespace='concierge')),
    url(r'', include('main.urls', namespace='main')),
    url(r'', include('payment.urls', namespace='payment')),
    url(r'', include('sms.urls', namespace='sms')),
    
    # DRF
    url(r'^api/', include(router.urls)),
    url(r'api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # My DRF (Non-ViewSet Endpoints)
    url(r'^api/current-user/$', CurrentUserAPIView.as_view()),

    # Textress Views
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^terms-and-conditions/$', views.TermsNCondView.as_view(), name='terms_n_cond'),
    url(r'^404/$', views.handler404, name='404'),
    url(r'^500/$', views.handler500, name='500'),
)

handler404 = 'textress.views.handler404'
handler500 = 'textress.views.handler500'

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes':True}),
)
