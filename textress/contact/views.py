from django.shortcuts import render
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import CreateView
from django.http import HttpResponseRedirect

from rest_framework.response import Response
from rest_framework import generics, permissions

from contact import tasks
from contact.models import Contact, Topic, Newsletter
from contact.forms import ContactForm, NewsletterForm
from contact.serializers import ContactSerializer
from contact.mixins import NewsletterMixin, TwoFormMixin
from utils.messages import dj_messages
from utils.email import Email


class ComingSoonView(CreateView):
    '''
    Landing page for Launch of site.
    '''
    template_name = 'biz/coming_soon.html'
    form_class = NewsletterForm
    model = Newsletter
    fields = ['email']
    success_url = reverse_lazy('contact:coming_soon')

    def form_valid(self, form):
        super(ComingSoonView, self).form_valid(form)
        messages.info(self.request, dj_messages['coming_soon'])
        
        # dispatch to Celery
        obj = Newsletter.objects.get(email=form.cleaned_data['email'])

        ## comment out to test w/o redis/rabbitmq
        # tasks.send_email.delay(
        #     to=obj.email,
        #     subject='email/coming_soon_subject.txt',
        #     html_content='email/coming_soon_email.html'
        #     )
        
        # send email w/o Celery
        email = Email(
            to=obj.email,
            subject='email/coming_soon_subject.txt',
            html_content='email/coming_soon_email.html'
        )
        email.msg.send()

        return HttpResponseRedirect(self.get_success_url())


########
# REST #
########

class ContactListCreateAPIView(generics.ListCreateAPIView):
    '''Admin Only Access For connecting with AngJs Contact form 
    and testing Token Auth.'''

    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    # permission_classes = (permissions.IsAdminUser,)

    def list(self, request, *args, **kwargs):
        '''For JSON Encoding.'''

        serializer = ContactSerializer(self.queryset, many=True)
        return Response(serializer.data)