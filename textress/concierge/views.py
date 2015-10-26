from django.conf import settings
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import View, DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.db.models import Q

from braces.views import (LoginRequiredMixin, SetHeadlineMixin, CsrfExemptMixin,
    StaticContextMixin)
from rest_framework import generics, permissions, viewsets
from rest_framework.decorators import list_route
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from twilio import twiml
from ws4redis.redis_store import RedisMessage
from ws4redis.publisher import RedisPublisher

from concierge.models import Message, Guest, Reply, TriggerType, Trigger
from concierge.helpers import process_incoming_message, convert_to_json_and_publish_to_redis
from concierge.forms import GuestForm
from concierge.mixins import GuestListContextMixin
from concierge.permissions import IsHotelObject, IsManagerOrAdmin, IsHotelUser
from concierge.serializers import (MessageListCreateSerializer, GuestMessageSerializer,
    GuestListSerializer, MessageRetrieveSerializer, ReplySerializer,
    TriggerTypeSerializer, TriggerSerializer, TriggerCreateSerializer)
from concierge.tasks import check_twilio_messages_to_merge
from main.mixins import HotelUserMixin, HotelObjectMixin
from utils import EmptyForm, DeleteButtonMixin
from utils.views import BaseModelViewSet


class ReceiveSMSView(CsrfExemptMixin, TemplateView):
    '''
    Main SMS Receiving endpoint for url to be configured on Twilio.
    '''
    template_name = 'blank.html'

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ReceiveSMSView, self).dispatch(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, 'blank.html', content_type="text/xml")

    def post(self, request, *args, **kwargs):
        # must return this to confirm SMS received for Twilio API
        resp = twiml.Response()
        # if a msg is returned, attach and reply to Guest
        msg, reply = process_incoming_message(data=request.POST)
        # Incoming Message from Guest
        convert_to_json_and_publish_to_redis(msg)
        # Auto-reply Logic
        if reply and reply.message:
            resp.message(reply.message)
            client = msg.guest.hotel._client
            # delay 5 seconds, query Twilio for this Guest, and find any 
            # missing SMS for Today, and merge them into the DB            
            check_twilio_messages_to_merge.apply_async(
                (msg.guest,),
                countdown=5
            )

        return HttpResponse(str(resp), content_type='text/xml')


###############
# GUEST VIEWS #
###############

class GuestBaseView(SetHeadlineMixin, LoginRequiredMixin, HotelUserMixin, View):
    headline = "Guest View"
    model = Guest


class GuestListView(GuestBaseView, ListView):
    '''
    Angular View
    ------------
    Lists all Guests w/ links for Detail, Update, Delete.
    '''
    headline = "Guest List"


class GuestDetailView(GuestBaseView, GuestListContextMixin, DetailView):
    '''
    Angular View
    ------------
    Guest Message View to Send/Receive SMS from.
    '''
    def get(self, request, *args, **kwargs):
        """All Messages should be marked as 'read=True' when the User 
        goes to the Guests' DetailView."""
        self.object = self.get_object()
        Message.objects.filter(guest=self.object, read=False).update(read=True)

        # test block
        from concierge.tasks import check_twilio_messages_to_merge
        check_twilio_messages_to_merge(self.object)

        return super(GuestDetailView, self).get(request, *args, **kwargs)

    def get_headline(self):
        return u"{} Detail".format(self.object)

    def get_context_data(self, **kwargs):
        context = super(GuestDetailView, self).get_context_data(**kwargs)
        context.update(groups=Group.objects.all())
        return context

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(GuestDetailView, self).dispatch(*args, **kwargs)


class GuestCreateView(GuestBaseView, GuestListContextMixin, CreateView):
    
    headline = "Add a Guest"
    template_name = 'cpanel/form.html'
    model = Guest
    form_class = GuestForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.hotel = self.hotel
        self.object.save()
        Trigger.objects.send_message(self.object.id, "check_in")
        return super(GuestCreateView, self).form_valid(form)


class GuestUpdateView(GuestBaseView, GuestListContextMixin, UpdateView):

    headline = "Update Guest"
    template_name = 'cpanel/form.html'
    model = Guest
    form_class = GuestForm

    def get_form_kwargs(self):
        "Set Guest as a form attr."
        kwargs = super(GuestUpdateView, self).get_form_kwargs()
        kwargs['guest'] = self.object
        return kwargs  


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
        context['addit_info'] = "<div><h1 class='lead'>Are you sure that you want to delete \
        <strong>{}</strong>?</h1></div>".format(self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = Guest.objects.get(pk=kwargs['pk'])
        self.object.delete()
        return HttpResponseRedirect(reverse('concierge:guest_list'))


class ReplyView(IsManagerOrAdmin, SetHeadlineMixin, StaticContextMixin,
    HotelUserMixin, TemplateView):
    """
    :Angular View: Handle all Reply create/edit/delete UI.
    """
    headline = "Auto Replies"
    template_name = "concierge/replies.html"
    static_context = {'headline_small': '& Automatic Messaging'}


########
# REST #
########

### MESSAGE ###

DEFAULT_PERMISSIONS = (permissions.IsAuthenticated, IsManagerOrAdmin, IsHotelObject,)


class MessageListCreateAPIView(generics.ListCreateAPIView):
    "All Messages records for a single Hotel."
    
    queryset = Message.objects.all()
    serializer_class = MessageListCreateSerializer
    permission_classes = DEFAULT_PERMISSIONS

    def list(self, request):
        "The User can only view their Hotel's Messages."
        messages = Message.objects.filter(guest__hotel=request.user.profile.hotel)
        serializer = MessageListCreateSerializer(messages, many=True)
        return Response(serializer.data)


class MessageRetrieveAPIView(generics.RetrieveUpdateAPIView):

    queryset = Message.objects.all()
    serializer_class = MessageRetrieveSerializer
    permission_classes = DEFAULT_PERMISSIONS


### GUEST ###

class GuestMessageListAPIView(generics.ListAPIView):
    """Filter for Guests for the User's Hotel only."""
    queryset = Guest.objects.all()
    serializer_class = GuestMessageSerializer
    permission_classes = DEFAULT_PERMISSIONS

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
    permission_classes = DEFAULT_PERMISSIONS


class GuestListCreateAPIView(generics.ListCreateAPIView):
    '''
    Returns only Guests from the Users' Hotel. Don't need to filter 
    for this in the AngJs Service.
    '''

    queryset = Guest.objects.all()
    serializer_class = GuestListSerializer
    permission_classes = DEFAULT_PERMISSIONS

    def list(self, request):
        guests = Guest.objects.filter(hotel=request.user.profile.hotel)
        serializer = GuestListSerializer(guests, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(hotel=self.request.user.profile.hotel)


class GuestRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):

    queryset = Guest.objects.all()
    serializer_class = GuestListSerializer
    permission_classes = DEFAULT_PERMISSIONS


### REPLY

class ReplyAPIView(BaseModelViewSet):

    queryset = Reply.objects.all()
    serializer_class = ReplySerializer
    permission_classes = DEFAULT_PERMISSIONS
    model = Reply
    filter_fields = [f.name for f in model._meta.get_fields()]

    def get_queryset(self):
        queryset = super(ReplyAPIView, self).get_queryset()

        queryset = queryset.filter(
            Q(hotel=self.request.user.profile.hotel) | \
            Q(hotel__isnull=True)
        )
        return queryset

    @list_route(methods=['GET'], url_path=r'hotel-letters')
    def all_hotel_letters(self, request):
        from concierge.models import REPLY_LETTERS
        return Response([x[0] for x in REPLY_LETTERS 
                           if x[0] not in settings.RESERVED_REPLY_LETTERS])


class TriggerTypeAPIView(BaseModelViewSet):

    queryset = TriggerType.objects.all()
    serializer_class = TriggerTypeSerializer
    permission_classes = (permissions.IsAuthenticated, IsManagerOrAdmin,)


class TriggerAPIView(BaseModelViewSet):

    queryset = Trigger.objects.all()
    serializer_class = TriggerSerializer
    permission_classes = DEFAULT_PERMISSIONS
    model = Trigger
    filter_fields = [f.name for f in model._meta.get_fields()]

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return TriggerCreateSerializer
        else:
            return TriggerSerializer

    def get_queryset(self):
        queryset = super(TriggerAPIView, self).get_queryset()
        queryset = queryset.filter(hotel=self.request.user.profile.hotel)
        return queryset
