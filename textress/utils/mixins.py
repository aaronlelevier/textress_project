from django.views.generic import View

from rest_framework import status
from rest_framework.response import Response

from braces.views import FormValidMessageMixin


class DeleteButtonMixin(object):
    "Color and Text for a Delete Button to display to User."

    def get_context_data(self, **kwargs):
        context = super(DeleteButtonMixin, self).get_context_data(**kwargs)
        context['btn_color'] = 'danger'
        context['btn_text'] = 'Delete'
        return context


class BreadcrumbBaseMixin(object):
    """Base Class for creating a breadcrumb widget in a View. 
    Override in ``__init__`` only."""

    def __init__(self):
        self.clip_icon = None
        self.url = None
        self.url_name = None

    def get_context_data(self, **kwargs):
        context = super(BreadcrumbBaseMixin, self).get_context_data(**kwargs)
        context['breadcrumbs'] = '''
        <li>
            <i class="{clip_icon}"></i>
            <a href="{url}">
                {url_name}
            </a>
        </li>'''.format(clip_icon=self.clip_icon, url=self.url, url_name=self.url_name)
        return context


class FormUpdateMessageMixin(FormValidMessageMixin, View):

    def get_form_valid_message(self):
        return "{0} Updated".format(self.headline)


class DestroyModelMixin(object):
    """
    Pass `override` kwarg to do a permanent ``delete``, else ``hide``.
    """
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        override = request.data.get('override', None)
        self.perform_destroy(instance, override)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance, override):
        instance.delete(override)
