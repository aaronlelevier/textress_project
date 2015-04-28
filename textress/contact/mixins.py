from django.views.generic.edit import FormMixin
from django.core.urlresolvers import reverse, reverse_lazy

from braces.views import FormValidMessageMixin

from contact.forms import NewsletterForm


class NewsletterMixin(FormValidMessageMixin, FormMixin):

    form_class = NewsletterForm
    success_url = reverse_lazy('main:index')
    form_valid_message = "Thank you for signing up for our monthly newsletter"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nl_form'] = self.get_form_class()
        return context


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