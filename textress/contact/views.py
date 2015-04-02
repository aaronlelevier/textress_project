from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView

from contact.forms import NewsletterForm
from contact.models import Newsletter
from utils.messages import dj_messages


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

    def form_valid(self, form):
        messages.info(self.request, dj_messages['coming_soon'])
        return super().form_valid(form)