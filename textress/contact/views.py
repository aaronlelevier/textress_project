from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView
from django.http import HttpResponseRedirect

from contact import tasks
from contact.forms import NewsletterForm
from contact.models import Newsletter
from utils.messages import dj_messages
from utils import email


class ComingSoonView(CreateView):
    '''
    NEXT
    ----
    write tests
    Change Template verbiage to "Textress"
    coming_soon date = Jun 21st
    change to use a Django Form in Template
    '''

    template_name = 'biz/coming_soon.html'
    form_class = NewsletterForm
    model = Newsletter
    fields = ['email']
    success_url = reverse_lazy('contact:coming_soon')

    def get(self, request, *args, **kwargs):
        tasks.hello_world.delay()
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        super().form_valid(form)
        messages.info(self.request, dj_messages['coming_soon'])
        
        # dispatch to Celery
        obj = Newsletter.objects.get(email=form.cleaned_data['email'])
        email.send(obj)

        return HttpResponseRedirect(self.get_success_url())