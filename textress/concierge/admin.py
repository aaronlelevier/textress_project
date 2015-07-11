from django import forms
from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea

from concierge.models import Guest, Message, Reply

@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'hotel',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('pk', 'guest', 'created', 'body',)
    readonly_fields = ('created',)


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'letter', 'message', 'func_call',)
    readonly_fields = ('created', 'modified')
