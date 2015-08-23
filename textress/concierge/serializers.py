from rest_framework import serializers
from django.contrib.auth.models import User

from concierge.models import Guest, Message


### MESSAGE

class MessageGuestUserSerializer(serializers.ModelSerializer):
    '''So that Guest serializers w/ messages don't show the same 
    Guest twice.'''

    class Meta:
        model = Message
        fields = ('id', 'guest', 'user', 'read',)


class MessageBasicSerializer(serializers.ModelSerializer):
    '''So that Guest serializers w/ messages don't show the same 
    Guest twice.'''

    class Meta:
        model = Message
        fields = ('id', 'guest', 'user', 'sid', 'received', 'status',
            'to_ph', 'from_ph', 'body', 'reason', 'cost', 'read',
            'created', 'modified', 'hidden')
        read_only_fields = ('created', 'modified',)


class MessageSerializer(serializers.ModelSerializer):
    
    guest = serializers.PrimaryKeyRelatedField(
        queryset=Guest.objects.all(),
        required=False
        )
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        required=False
        )

    class Meta:
        model = Message
        fields = ('id', 'guest', 'user', 'sid', 'received', 'status',
            'to_ph', 'from_ph', 'body', 'reason', 'cost', 'read',
            'created', 'modified', 'insert_date', 'hidden')
        read_only_fields = ('created', 'modified',)


### GUEST

class GuestBasicSerializer(serializers.ModelSerializer):
    '''Currently only used to support MessageSerializer as a 
    Nested Serializer.'''
    messages = MessageGuestUserSerializer(many=True, source='message_set')

    class Meta:
        model = Guest
        fields = ('id', 'name', 'room_number', 'phone_number', 'thumbnail',
            'check_in', 'check_out', 'created', 'modified', 'hidden',
            'messages',)
        read_only_fields = ('created', 'modified',)


class GuestMessageSerializer(serializers.ModelSerializer):
    messages = MessageBasicSerializer(many=True, source='message_set')

    class Meta:
        model = Guest
        fields = ('id', 'name', 'room_number', 'phone_number', 'thumbnail',
            'check_in', 'check_out', 'created', 'modified', 'hidden',
            'messages')
        read_only_fields = ('created', 'modified',)