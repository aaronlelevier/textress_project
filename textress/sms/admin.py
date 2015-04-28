from django import forms
from django.contrib import admin
from django.db import models
from django.forms import TextInput, Textarea

from sms.models import Text, DemoCounter, PhoneNumber


class TextForm(forms.ModelForm):

    class Meta:
        model = Text


class TextAdmin(admin.ModelAdmin):
    form = TextForm
    search_fields = ['body']
    list_display = ('created', 'sent', 'to', 'frm', 'body',)
    readonly_fields = ('created',)
    fieldsets = [
        ('Info', {'fields': ['sent', 'to', 'frm']}),
        ('Body', {'fields': ['body']}),
        ('Auto Fields', {'fields': ['created']})
    ]


class DemoCounterAdmin(admin.ModelAdmin):
    search_fields = ['day']
    list_display = ('day', 'count')


class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'friendly_name', 'sid',)

    
admin.site.register(Text, TextAdmin)
admin.site.register(DemoCounter, DemoCounterAdmin)
admin.site.register(PhoneNumber, PhoneNumberAdmin)