from django.shortcuts import render
from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView

from contact.forms import NewsletterForm
from contact.models import Newsletter


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
    # form_class = NewsletterForm
    success_url = reverse_lazy('main:coming_soon')
    model = Newsletter
    fields = ['email']