from django import forms
from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea

from concierge.models import Guest, Message, Reply


class GuestAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'hotel',)


class MessageAdmin(admin.ModelAdmin):
    list_display = ('pk', 'guest', 'created', 'body',)
    readonly_fields = ('created',)


class ReplyAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'letter', 'message', 'func_call',)
    readonly_fields = ('created', 'modified')


admin.site.register(Guest, GuestAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Reply, ReplyAdmin)