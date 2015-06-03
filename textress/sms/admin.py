from django.contrib import admin

from sms.models import PhoneNumber


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'friendly_name', 'sid',)
