from django.db import models
from django.contrib import admin
from django.forms.widgets import TextInput

from contact.models import Contact, Topic, QA


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    pass


@admin.register(QA)
class QAAdmin(admin.ModelAdmin):
    list_display = fields = ('topic', 'order', 'question', 'answer')
    formfield_overrides = {
            models.CharField: {'widget': TextInput(attrs={'size':'100'})},
        }