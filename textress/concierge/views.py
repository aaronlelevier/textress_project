import json
import re
import datetime
from collections import OrderedDict
import twilio
from twilio import twiml, TwilioRestException 

from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.views.generic import View, FormView, DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from django.http import HttpResponse
from django.utils import timezone
from django.forms.models import model_to_dict

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework import mixins, generics, status, permissions, viewsets

from braces.views import (LoginRequiredMixin, PermissionRequiredMixin,
    GroupRequiredMixin, SetHeadlineMixin, FormValidMessageMixin, CsrfExemptMixin)

from ws4redis.redis_store import RedisMessage
from ws4redis.publisher import RedisPublisher

from concierge.models import Message, Guest
from concierge.helpers import process_incoming_message
from concierge.forms import GuestForm
from concierge.permissions import IsHotelObject, IsManagerOrAdmin, IsHotelUser
from concierge.serializers import (MessageSerializer, GuestMessageSerializer,
    GuestBasicSerializer)
from sms.helpers import send_text, send_message, sms_messages
from main.models import Hotel, UserProfile
from main.mixins import HotelUserMixin, HotelObjectMixin
from utils.exceptions import (DailyLimit, NotHotelGuestException,
    HotelGuestNotFoundException)
from utils import EmptyForm, DeleteButtonMixin


class ReceiveSMSView(CsrfExemptMixin, TemplateView):
    '''
    Main SMS Receiving endpoint for url to be configured on Twilio.
    '''

    template_name = 'blank.html'

    def get(self, request, *args, **kwargs):
        return render(request, 'blank.html', content_type="text/xml")

    def post(self, request, *args, **kwargs):
        # must return this to confirm SMS received for Twilio API
        resp = twiml.Response()

        # if a msg is returned, attach and reply to Guest
        msg, reply, hotel = process_incoming_message(data=request.POST)
        if reply:
            resp.message(reply)

        # convert to JSON, and publish to Redis
        redis_publisher = RedisPublisher(facility='foobar', broadcast=True)
        msg = JSONRenderer().render(model_to_dict(msg))
        msg = RedisMessage(msg)
        redis_publisher.publish_message(msg)

        return render(request, 'blank.html', {'resp': str(resp)},
            content_type='text/xml')

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ReceiveSMSView, self).dispatch(*args, **kwargs)


###############
# GUEST VIEWS #
###############

class GuestBaseView(SetHeadlineMixin, HotelUserMixin, View):
    headline = "Guest View"
    model = Guest


class GuestListView(GuestBaseView, ListView):
    '''
    Angular View
    ------------
    Lists all Guests w/ links for Detail, Update, Delete.
    '''
    headline = "Guest List"


class GuestDetailView(GuestBaseView, DetailView):
    '''
    Angular View
    ------------
    Guest Message View to Send/Receive SMS from.
    '''
    def get_headline(self):
        return u"{} Detail".format(self.object)

    def get_context_data(self, **kwargs):
        context = super(GuestDetailView, self).get_context_data(**kwargs)
        context.update(groups=Group.objects.all())
        return context

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(GuestDetailView, self).dispatch(*args, **kwargs)


class GuestCreateView(GuestBaseView, CreateView):
    
    headline = "Add a Guest"
    template_name = 'cpanel/form.html'
    model = Guest
    form_class = GuestForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.hotel = self.hotel
        self.object.save()
        return super(GuestCreateView, self).form_valid(form)


class GuestUpdateView(GuestBaseView, UpdateView):
    '''
    TODO
    ----
    Add Js ph # prettifier
    '''
    headline = "Update Guest"
    template_name = 'cpanel/form.html'
    model = Guest
    form_class = GuestForm      


class GuestDeleteView(GuestBaseView, DeleteButtonMixin, TemplateView):
    '''
    Hide only. Don't `delete` any guest records b/c don't want to
    delete the related `Messages`.
    '''
    headline = "Delete Guest"
    template_name = 'cpanel/form.html'

    def get_context_data(self, **kwargs):
        context = super(GuestDeleteView, self).get_context_data(**kwargs)
        self.object = Guest.objects.get(pk=kwargs['pk'])
        context['addit_info'] = "<div><h4>Are you sure that you want to delete \
        {}?</h4></div>".format(self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = Guest.objects.get(pk=kwargs['pk'])
        self.object.hide()
        return HttpResponseRedirect(reverse('concierge:guest_list'))


########
# REST #
########

### MESSAGE ###

class MessageListCreateAPIView(generics.ListCreateAPIView):
    
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated, IsManagerOrAdmin, IsHotelObject,)

    def list(self, request, *args, **kwargs):
        """
        Message records for the User's Hotel. (Same for all Viewsets)
        try/except because AnonymousUser has no 'profile' attr.
        """
        try:
            messages = Message.objects.filter(guest__hotel=request.user.profile.hotel)
        except AttributeError:
            raise Http404
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MessageRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated, IsManagerOrAdmin, IsHotelObject,)


### GUEST ###

class GuestMessageListAPIView(generics.ListAPIView):
    """Filter for Guests for the User's Hotel only."""
    queryset = Guest.objects.all()
    serializer_class = GuestMessageSerializer
    permission_classes = (permissions.IsAuthenticated, IsManagerOrAdmin, IsHotelObject,)

    def list(self, request):
        try:
            guests = Guest.objects.filter(hotel=request.user.profile.hotel)
        except AttributeError:
            raise Http404
        serializer = GuestMessageSerializer(guests, many=True)
        return Response(serializer.data)


class GuestMessageRetrieveAPIView(generics.RetrieveAPIView):

    queryset = Guest.objects.all()
    serializer_class = GuestMessageSerializer
    permission_classes = (permissions.IsAuthenticated, IsManagerOrAdmin, IsHotelObject,)


class GuestListCreateAPIView(generics.ListCreateAPIView):
    '''
    Returns only Guests from the Users' Hotel. Don't need to filter 
    for this in the AngJs Service.
    '''

    queryset = Guest.objects.all()
    serializer_class = GuestBasicSerializer
    permission_classes = (permissions.IsAuthenticated, IsManagerOrAdmin, IsHotelObject,)

    def list(self, request):
        guests = Guest.objects.current().filter(hotel=request.user.profile.hotel)
        serializer = GuestBasicSerializer(guests, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(hotel=self.request.user.profile.hotel)


class GuestRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):

    queryset = Guest.objects.all()
    serializer_class = GuestBasicSerializer
    permission_classes = (permissions.IsAuthenticated, IsManagerOrAdmin, IsHotelObject,)
