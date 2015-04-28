import six

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpResponseRedirect
from django.utils.encoding import force_text


class AnonymousRequiredMixin(object):
    """
    View mixin which redirects to a specified URL if authenticated.
    Can be useful if you wanted to prevent authenticated users from
    accessing signup pages etc.

    NOTE:
        This should be the left-most mixin of a view.

    Example Usage

        class SomeView(AnonymousRequiredMixin, ListView):
            ...
            # required
            authenticated_redirect_url = "/accounts/profile/"
            ...
    """
    authenticated_redirect_url = settings.LOGIN_REDIRECT_URL

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(self.get_authenticated_redirect_url())
        return super().dispatch(request, *args, **kwargs)

    def get_authenticated_redirect_url(self):
        """ Return the reversed authenticated redirect url. """
        if not self.authenticated_redirect_url:
            raise ImproperlyConfigured(
                '{0} is missing an authenticated_redirect_url '
                'url to redirect to. Define '
                '{0}.authenticated_redirect_url or override '
                '{0}.get_authenticated_redirect_url().'.format(
                    self.__class__.__name__))
        return self.authenticated_redirect_url