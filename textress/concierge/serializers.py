from rest_framework import serializers
from django.contrib.auth.models import User

from .models import Guest, Message


### SUPPORT SERIALIZERS ###

class GuestBasicSerializer(serializers.ModelSerializer):
    '''Currently only used to support MessageSerializer as a 
    Nested Serializer.'''

    class Meta:
        model = Guest
        fields = ('id', 'name', 'room_number', 'phone_number',
            'check_in', 'check_out', 'created', 'modified', 'hidden')
        read_only_fields = ('created', 'modified',)


class MessageBasicSerializer(serializers.ModelSerializer):
    '''So that Guest serializers w/ messages don't show the same 
    Guest twice.'''

    class Meta:
        model = Message
        fields = ('id', 'guest', 'user', 'sid', 'received', 'status',
            'to_ph', 'from_ph', 'body', 'reason', 'cost', 'read',
            'created', 'modified', 'hidden')
        read_only_fields = ('created', 'modified',)


### PRODUCTION SERIALIZERS ###

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
        read_only_fields = ('id', 'username',)


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
        

class GuestMessageSerializer(serializers.ModelSerializer):
    messages = MessageBasicSerializer(many=True, source='message_set')

    class Meta:
        model = Guest
        fields = ('id', 'name', 'room_number', 'phone_number',
            'check_in', 'check_out', 'created', 'modified', 'hidden',
            'messages')
        read_only_fields = ('created', 'modified',)