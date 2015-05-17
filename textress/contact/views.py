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
from contact.serializers import ContactSerializer, FAQSerializer
from contact.mixins import NewsletterMixin, TwoFormMixin
from utils.messages import dj_messages
from utils.email import Email



########
# REST #
########

class FAQListAPIView(generics.ListAPIView):
    '''No permissions needed b/c read only list view, and will be used 
    on the Biz Site.'''

    queryset = Topic.objects.all()
    serializer_class = FAQSerializer

    def list(self, request, *args, **kwargs):
        '''For JSON Encoding.'''

        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)

class FAQRetrieveAPIView(generics.RetrieveAPIView):

    queryset = Topic.objects.all()
    serializer_class = FAQSerializer


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