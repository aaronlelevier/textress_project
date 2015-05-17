from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import CreateView, TemplateView, FormView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect

from contact.forms import ContactForm
from contact.models import Contact
from utils.messages import dj_messages
from utils.email import Email


class PricingView(TemplateView):
    template_name = 'frontend/pricing.html'


class IndexView(CreateView):
    '''
    ContactForm / FAQs Model data 

    TODO
    ----
    make google map not scroll or skinnier
    test CreateView on server side
    change sent email templates b/c no longer "coming soon"
    FAQ <section> still needs to be added n data w/ that as wel
    '''

    template_name = 'frontend/index.html'
    form_class = ContactForm
    model = Contact
    fields = ['name', 'email', 'subject', 'message']
    success_url = reverse_lazy('index')

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        messages.info(self.request, dj_messages['contact_not_sent'])
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        super(IndexView, self).form_valid(form)
        messages.info(self.request, dj_messages['contact_thanks'])
        
        obj = Contact.objects.get(**form.cleaned_data)
        
        email = Email(
            to=obj.email,
            subject='email/contact_subject.txt',
            html_content='email/contact_email.html'
        )
        email.msg.send()

        return HttpResponseRedirect(self.get_success_url())


class TermsNCondView(TemplateView):
    template_name = 'frontend/terms_n_cond.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['company'] = "Textress"
        context['LLC'] = "Aronysidoro LLC."
        return context


def handler404(request):
    response = render_to_response('error/404.html', {},
        context_instance=RequestContext(request))
    response.status_code = 404
    return response


def handler500(request):
    response = render_to_response('error/500.html', {},
        context_instance=RequestContext(request))
    response.status_code = 500
    return response