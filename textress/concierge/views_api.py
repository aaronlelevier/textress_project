from django.conf import settings
from django.http import Http404
from django.db.models import Q

from rest_framework import permissions, viewsets
from rest_framework.decorators import list_route
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from concierge.models import Message, Guest, Reply, TriggerType, Trigger
from concierge.permissions import IsHotelObject, IsManagerOrAdmin
from concierge.serializers import (MessageListCreateSerializer, GuestMessageSerializer,
    GuestListSerializer, MessageRetrieveSerializer, ReplySerializer,
    TriggerTypeSerializer, TriggerSerializer, TriggerCreateSerializer)
from utils.views import BaseModelViewSet


DEFAULT_PERMISSIONS = (permissions.IsAuthenticated, IsManagerOrAdmin, IsHotelObject,)


class MessageAPIView(viewsets.ModelViewSet):
    
    queryset = Message.objects.current()
    permission_classes = DEFAULT_PERMISSIONS

    def get_serializer_class(self):
        if self.action in ('create', 'list'):
            return MessageListCreateSerializer
        elif self.action in ('retrieve', 'update', 'partial_update'):
            return MessageRetrieveSerializer
        else:
            raise MethodNotAllowed(self.action)

    def list(self, request):
        "The User can only view their Hotel's Messages."
        messages = Message.objects.current().filter(guest__hotel=request.user.profile.hotel)
        serializer = MessageListCreateSerializer(messages, many=True)
        return Response(serializer.data)


class GuestMessagesAPIView(viewsets.ModelViewSet):
    """Filter for Guests for the User's Hotel only."""

    queryset = Guest.objects.current()
    permission_classes = DEFAULT_PERMISSIONS

    def list(self, request):
        try:
            guests = Guest.objects.current().filter(hotel=request.user.profile.hotel)
        except AttributeError:
            raise Http404
        serializer = GuestMessageSerializer(guests, many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return GuestMessageSerializer
        else:
            raise MethodNotAllowed(self.action)


class GuestAPIView(viewsets.ModelViewSet):

    queryset = Guest.objects.current()
    permission_classes = DEFAULT_PERMISSIONS

    def list(self, request):
        guests = Guest.objects.current().filter(hotel=request.user.profile.hotel)
        serializer = GuestListSerializer(guests, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(hotel=self.request.user.profile.hotel)

    def get_serializer_class(self):
        if self.action == 'list':
            return GuestListSerializer
        else:
            raise MethodNotAllowed(self.action)


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


class CurrentUserAPIView(APIView):
    
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, format='json'):
        try:
            data = {
                'id': request.user.id,
                'hotel_id': request.user.profile.hotel.id
            }
        except AttributeError:
            raise PermissionDenied

        return Response(data)
