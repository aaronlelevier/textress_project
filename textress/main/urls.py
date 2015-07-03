from django.conf.urls import patterns, include, url

from main import views


api_patterns = patterns('',
    url(r'^users/$', views.UserListCreateAPIView.as_view(), name='api_users'),
    url(r'^users/(?P<pk>\d+)/$', views.UserRetrieveUpdateAPIView.as_view(), name='api_users'),
    )

register_patterns = patterns('',
    # Step 1
    url(r'^step1/$', views.RegisterAdminCreateView.as_view(), name='register_step1'),
    url(r'^step1/update/(?P<pk>\d+)/$', views.RegisterAdminUpdateView.as_view(), name='register_step1_update'),
    # Step 2
    url(r'^step2/$', views.RegisterHotelCreateView.as_view(), name='register_step2'),
    url(r'^step2/update/(?P<pk>\d+)/$', views.RegisterHotelUpdateView.as_view(), name='register_step2_update'),
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
    # url(r'^(?P<pk>\d+)/$', views.UserDetailView.as_view(), name='user_detail'),
    url(r'^update/(?P<pk>\d+)/$', views.UserUpdateView.as_view(), name='user_update'),
    )

hotel_patterns = patterns('',
    url(r'^update/(?P<pk>\d+)/$', views.HotelUpdateView.as_view(), name='hotel_update'),
    )

urlpatterns = patterns('',
    url(r'^api/', include(api_patterns)),
    url(r'^register/', include(register_patterns)),
    url(r'^account/user/', include(user_patterns)),
    url(r'^account/hotel/', include(hotel_patterns)),
    url(r'^account/manage-users/', include(manage_users_patterns)),
    )
