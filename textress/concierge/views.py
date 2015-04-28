import json
import re
import datetime
from collections import OrderedDict
import twilio
from twilio import twiml, TwilioRestException 

from django.contrib.auth.models import User
from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.views.generic import View, FormView, DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt, csrf_protect, ensure_csrf_cookie
from django.http import HttpResponse
from django.utils import timezone

from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response
from rest_framework import mixins, generics, status, permissions, viewsets

from braces.views import (LoginRequiredMixin, PermissionRequiredMixin,
    CsrfExemptMixin)

from .models import Message, Guest
from .helpers import process_incoming_message
from .forms import MessageForm
from .permissions import IsHotelObject, IsManagerOrAdmin, IsHotelUser
from .serializers import (
    MessageSerializer,
    GuestMessageSerializer,
    GuestBasicSerializer,
    UserSerializer
    )

from sms.helpers import send_text, send_message, sms_messages
from main.models import Hotel, UserProfile
from main.views import HotelMixin
from payment.views import HotelUserMixin
from utils.exceptions import (DailyLimit, NotHotelGuestException,
    HotelGuestNotFoundException)


class ReceiveSMSView(CsrfExemptMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, 'blank.html', content_type="text/xml")

    def post(self, request, *args, **kwargs):
        resp = twiml.Response()

        # if a msg is returned, attach and reply to Guest
        msg = process_incoming_message(data=request.POST)
        if msg:
            resp.message(msg)

        return render(request, 'blank.html', {'resp': str(resp)},
            content_type='text/xml')


###############
# GUEST VIEWS #
###############

class GuestListView(HotelUserMixin, ListView):
    model = Guest

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = self.model.objects.current().filter(
            hotel=self.hotel)
        return context


class GuestDetailView(HotelUserMixin, DetailView):
    model = Guest


class GuestCreateView(HotelUserMixin, CreateView):
    model = Guest
    fields = ['name', 'room_number', 'phone_number', 'check_in', 'check_out']

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.hotel = self.hotel
        self.object.save()
        hotel, created = Hotel.objects.get_or_create(guest=self.object)
        return super().form_valid(form)


class GuestUpdateView(HotelUserMixin, UpdateView):
    '''
    TODO
    ----
    Add Js ph # prettifier
    '''
    model = Guest
    fields = ['name', 'room_number', 'phone_number', 'check_in', 'check_out']


class GuestDeleteView(HotelUserMixin, View):
    '''Hide only. Don't `delete` any guest records b/c don't want to
    delete the related `Messages`.'''

    template_name = 'concierge/guest_delete.html'

    def get(self, request, *args, **kwargs):
        self.object = Guest.objects.get(pk=kwargs['pk'])
        return render(request, self.template_name, {'object': self.object})

    def post(self, request, *args, **kwargs):
        self.object = Guest.objects.get(pk=kwargs['pk'])
        self.object.hide()
        return HttpResponseRedirect(reverse('concierge:guest_list'))


#################
# MESSAGE VIEWS #
#################

class MessageListView(HotelMixin, FormView):
    """
    All Messages for 1 Guest.
    A Form at the bottom to send new Messages.
    """
    form_class = MessageForm
    template_name = 'concierge/conversation_detail.html'

    def form_valid(self, form):
        cd = form.cleaned_data
        messages.info(self.request, sms_messages['sent'])
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        self.hotel = request.user.profile.hotel
        self.guest = get_object_or_404(Guest, pk=self.kwargs['pk'], hotel=self.hotel)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('concierge:message_list', kwargs={'pk':self.guest.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guest_messages'] = Message.objects.filter(guest=self.guest).order_by('created')
        return context


class MessageDetailView(HotelMixin, DetailView):
    model = Message


########
# REST #
########

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

    queryset = Guest.objects.all()
    serializer_class = GuestBasicSerializer
    permission_classes = (permissions.IsAuthenticated, IsManagerOrAdmin, IsHotelObject,)

    def list(self, request):
        guests = Guest.objects.filter(hotel=request.user.profile.hotel)
        serializer = GuestBasicSerializer(guests, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(hotel=self.request.user.profile.hotel)


class GuestRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):

    queryset = Guest.objects.all()
    serializer_class = GuestBasicSerializer
    permission_classes = (permissions.IsAuthenticated, IsManagerOrAdmin, IsHotelObject,)


class UserListCreateAPIView(generics.ListCreateAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsManagerOrAdmin,)

    def list(self, request):
        users = User.objects.filter(profile__hotel=request.user.profile.hotel)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def perform_update(self, serializer):
        user = serializer.save()
        user_profile = user.profile
        user_profile.update_hotel(hotel=self.request.profile.hotel)


class UserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsManagerOrAdmin, IsHotelUser)

