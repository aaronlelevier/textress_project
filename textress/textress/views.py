from django.contrib import messages
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import CreateView, TemplateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect

from contact.forms import NewsletterForm
from contact.models import Newsletter
from utils.messages import dj_messages
from utils.email import Email


class IndexView(CreateView):
    template_name = 'frontend/index.html'
    form_class = NewsletterForm
    model = Newsletter
    fields = ['email']
    success_url = reverse_lazy('contact:coming_soon')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nl_form'] = self.get_form_class()
        print(context['nl_form'])
        return context

    def form_valid(self, form):
        super(ComingSoonView, self).form_valid(form)
        messages.info(self.request, dj_messages['coming_soon'])
        
        obj = Newsletter.objects.get(email=form.cleaned_data['email'])
        
        email = Email(
            to=obj.email,
            subject='email/coming_soon_subject.txt',
            html_content='email/coming_soon_email.html'
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