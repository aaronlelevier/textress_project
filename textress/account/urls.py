from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views

from account import views
from account.forms import (AuthenticationForm, PasswordResetForm,
    SetPasswordForm, PasswordChangeForm)


register_patterns = patterns('',
    # Step 3
    url(r'^step3/$', views.RegisterAcctCostCreateView.as_view(), name='register_step3'),
    url(r'^step3/update/(?P<pk>\d+)/$', views.RegisterAcctCostUpdateView.as_view(), name='register_step3_update'),
    )

api_patterns = patterns('',
    url(r'^account/pricing/$', views.PricingListAPIView.as_view(), name='api_pricing'),
    url(r'^account/pricing/(?P<pk>\d+)/$', views.PricingRetrieveAPIView.as_view(), name='api_pricing'),
    )

acct_cost_patterns = patterns('',
    url(r'^refill-settings/(?P<pk>\w+)/$', views.AcctCostUpdateView.as_view(), name='acct_cost_update'),
    url(r'^history/$', views.AcctPmtHistoryView.as_view(), name='acct_pmt_history'),
)

acct_stmt_patterns = patterns('',
    url(r'^$', views.AcctStmtListView.as_view(), name='acct_stmt_list'),
    url(r'^(?P<year>\d+)/(?P<month>\d+)/$', views.AcctStmtDetailView.as_view(), name='acct_stmt_detail'),
    )

close_acct_patterns = patterns('',
    url(r'^$', views.CloseAcctView.as_view(), name='close_acct'),
    url(r'^confirm/(?P<slug>[-_\w]+)/$', views.CloseAcctConfirmView.as_view(), name='close_acct_confirm'),
    url(r'^submitted/$', views.CloseAcctSuccessView.as_view(), name='close_acct_success'),
    )

account_patterns = patterns('',
    # User Dashboard View
    url(r'^$', views.AccountView.as_view(), name='account'),

    # Auth Views
    url(r'^login/$',auth_views.login,
        {'template_name': 'cpanel/auth-forms/login.html',
        'authentication_form': AuthenticationForm},
        name='login'),

    ### 2 views for password change - when you are logged in and want to 
    ### change your password
    url(r'^password-change/$', auth_views.password_change,
        {'template_name': 'cpanel/auth-forms/password_change.html',
        'password_change_form': PasswordChangeForm},
        name='password_change'),

    url(r'^password-change/done/$', auth_views.password_change_done,
        {'template_name': 'cpanel/form-success/password_change_done.html'},
        name='password_change_done'),

    ### 4 views for password reset when you can't remember your password
    url(r'^password-reset/$', auth_views.password_reset,
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

    url(r'^password-reset/done/$', auth_views.password_reset_done,
        {'template_name': 'cpanel/form-success/password_reset_done.html'},
        name='password_reset_done'),

    url(r'^password-reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.password_reset_confirm,
        {'template_name':'cpanel/auth-forms/password_reset_confirm.html',
        'set_password_form': SetPasswordForm
        }, name='password_reset_confirm'),

    url(r'^password-reset/done/$', auth_views.password_reset_complete,
        {'template_name': 'cpanel/form-success/password_reset_complete.html'},
        name='password_reset_complete'),

    ### Textress Auth Views
    url(r'^verify-logout/$', views.verify_logout, name='verify_logout'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^private/$', views.private, name='private'),
    url(r'^login-error/$', views.login_error, name='login_error'),
)

urlpatterns = patterns('',
    url(r'^api/', include(api_patterns)),
    url(r'^account/', include(account_patterns)),
    url(r'^register/', include(register_patterns)),
    # Maybe ``payments`` will include other URL patterns besides ``AcctCost`` because
    # I may want to reuse the namespace for other URLs.
    url(r'^payments/', include(acct_cost_patterns)),
    url(r'^statements/', include(acct_stmt_patterns)),
    url(r'^close/', include(close_acct_patterns)),
    )