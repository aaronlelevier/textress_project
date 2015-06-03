from django.conf.urls import patterns, include, url

from sms import views


phone_patters = patterns('',
    url(r'^$', views.PhoneNumberListView.as_view(), name='ph_num_list'),
    url(r'^select/$', views.PhoneNumberSelectView.as_view(), name='ph_num_select'),
    # url(r'^add/$', views.PhoneNumberAddView.as_view(), name='ph_num_add'),
    )

urlpatterns = patterns('',
    url(r'^phone-numbers/', include(phone_patters)),
    )