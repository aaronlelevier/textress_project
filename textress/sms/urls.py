from django.conf.urls import patterns, include, url

from sms import views


phone_patters = patterns('',
    url(r'^$', views.PhoneNumberListView.as_view(), name='ph_num_list'),
    url(r'^add/$', views.PhoneNumberAddView.as_view(), name='ph_num_add'),
    url(r'^set-default(?P<pk>\w+)/$', views.set_default_phone_number_view, name='set_default_phone_number'),
    url(r'^delete/(?P<sid>[\w\d]+)/$', views.PhoneNumberDeleteView.as_view(), name='ph_num_delete'),
    )

urlpatterns = patterns('',
    url(r'^phone-numbers/', include(phone_patters)),
    )