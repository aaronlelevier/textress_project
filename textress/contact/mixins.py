from django.views.generic.edit import FormMixin
from django.core.urlresolvers import reverse_lazy

from braces.views import FormValidMessageMixin


class TwoFormMixin(object):

    form_class = None
    second_form_class = None

    def form_invalid(self, **kwargs):
        return self.render_to_response(self.get_context_data(**kwargs))

    def post(self, request, *args, **kwargs):
        if 'message' in request.POST:
            # get the primary form
            form_class = self.get_form_class()
            form_name = 'form'
        else:
            # get the secondary form
            form_class = self.second_form_class
            form_name = 'nl_form'
 
        # get the form
        form = self.get_form(form_class)
 
        # validate
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(**{form_name: form})