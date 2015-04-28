from rest_framework import serializers
from django.contrib.auth.models import User

from contact.models import Contact


class ContactSerializer(serializers.ModelSerializer):
    '''
    Business Homepage will be an Angular View, so use this for 
    the REST Endpoint for Contact Form submission.
    '''

    class Meta:
        model = Contact
        fields = ('id', 'name', 'email', 'subject', 'message')
        read_only_fields = ('created',)
