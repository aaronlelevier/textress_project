from rest_framework import serializers
from django.contrib.auth.models import User

from contact.models import Contact, Topic, QA


class ContactSerializer(serializers.ModelSerializer):
    '''
    Business Homepage will be an Angular View, so use this for 
    the REST Endpoint for Contact Form submission.
    '''

    class Meta:
        model = Contact
        fields = ('id', 'name', 'email', 'subject', 'message')
        read_only_fields = ('created',)


class QASerializer(serializers.ModelSerializer):
    
    class Meta:
        model = QA
        fields = ('id', 'topic', 'question', 'answer', 'order')



class FAQSerializer(serializers.ModelSerializer):
    qas = QASerializer(many=True, read_only=True)

    class Meta:
        model = Topic
        fields = ('id', 'name', 'fa_icon', 'slug', 'order', 'qas')