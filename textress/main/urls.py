from django.conf.urls import patterns, include, url

from main import views


register_patterns = patterns('',
    url(r'^step1/$', views.AdminCreateView.as_view(), name='register_step1'),
    url(r'^step2/$', views.HotelCreateView.as_view(), name='register_step2'),
    )

manage_users_patterns = patterns('',
    url(r'^$', views.MgrUserListView.as_view(), name='manage_user_list'),
    url(r'^(?P<pk>\d+)/$', views.MgrUserDetailView.as_view(), name='manage_user_detail'),
    url(r'^update/(?P<pk>\d+)/$', views.MgrUserUpdateView.as_view(), name='manage_user_update'),
    url(r'^delete/(?P<pk>\d+)/$', views.MgrUserDeleteView.as_view(), name='manage_user_delete'),
    url(r'^create-user/$', views.UserCreateView.as_view(), name='create_user'),
    url(r'^create-manager/$', views.ManagerCreateView.as_view(), name='create_manager'),
    )

user_patterns = patterns('',
    url(r'^(?P<pk>\d+)/$', views.UserDetailView.as_view(), name='user_detail'),
    url(r'^update/(?P<pk>\d+)/$', views.UserUpdateView.as_view(), name='user_update'),
    )

urlpatterns = patterns('',
    # Hotel
    url(r'^hotel/(?P<hotel_slug>[-_\w]+)/(?P<pk>\d+)/$', views.HotelDetailView.as_view(), name='hotel'),
    # Registration
    url(r'^register/', include(register_patterns)),
    url(r'^manage-users/', include(manage_users_patterns)),
    # Users
    url(r'^users/', include(user_patterns)),
    )



