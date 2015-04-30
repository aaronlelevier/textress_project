from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views

from account import views
from account.forms import (AuthenticationForm, PasswordResetForm, SetPasswordForm,
    PasswordChangeForm)


acct_stmt_patterns = patterns('',
    url(r'^$', views.AcctStmtListView.as_view(), name='acct_stmt_list'),
    url(r'^(?P<year>\d+)/(?P<month>\d+)/$', views.AcctStmtDetailView.as_view(), name='acct_stmt_detail'),
    )

close_acct_patterns = patterns('',
    url(r'^$', views.CloseAcctView.as_view(), name='close_acct'),
    url(r'^confirm/(?P<slug>[-_\w]+)/$', views.CloseAcctConfirmView.as_view(), name='close_acct_confirm'),
    url(r'^submitted/$', views.CloseAcctSuccessView.as_view(), name='close_acct_success'),
    )

urlpatterns = patterns('',
    # Main Profile View
    url(r'^$', views.AccountView.as_view(), name='account'),

    # Registration Views
    url(r'^login/$',auth_views.login,
        {'template_name': 'cpanel/auth-forms/login.html',
        'authentication_form': AuthenticationForm},
        name='login'),

    ### 2 views for password change - when you are logged in and want to 
    ### change your password

    url(r'^password_change/$', auth_views.password_change,
        {'template_name': 'cpanel/auth-forms/password_change.html',
        'password_change_form': PasswordChangeForm},
        name='password_change'),

    url(r'^password_change/done/$', auth_views.password_change_done,
        {'template_name': 'cpanel/form-success/password_change_done.html'},
        name='password_change_done'),

    ### 4 views for password reset - when you can't remember your password

    url(r'^password_reset/$', auth_views.password_reset,
        {
        'template_name': 'cpanel/auth-forms/password_reset.html',
        'email_template_name': 'email/password_reset.html',
        'subject_template_name': 'registration/password_reset_subject.txt',
        'password_reset_form': PasswordResetForm,
        'extra_context': {
            'headline': 'Forgot Password?'
            }
        },
        name='password_reset'),

    url(r'^password_reset/done/$', auth_views.password_reset_done,
        {'template_name': 'cpanel/form-success/password_reset_done.html'},
        name='password_reset_done'),

    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {'template_name':'cpanel/auth-forms/password_reset_confirm.html',
        'set_password_form': SetPasswordForm
        }, name='password_reset_confirm'),

    url(r'^reset/done/$', auth_views.password_reset_complete,
        {'template_name': 'cpanel/form-success/password_reset_complete.html'},
        name='password_reset_complete'),

    ### Textress Login Views ###

    # url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^verify-logout/$', views.verify_logout, name='verify_logout'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^private/$', views.private, name='private'),
    url(r'^login-error/$', views.login_error, name='login_error'),

    # TODO: move to another app =>

    url(r'^statements/', include(acct_stmt_patterns)),
    url(r'^close/', include(close_acct_patterns)),
    )