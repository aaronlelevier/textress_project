from django.contrib import admin

from concierge.models import Guest, Message, Reply, TriggerType, Trigger


@admin.register(Guest)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('name', 'pk', 'hotel', 'hidden',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('pk', 'guest', 'created', 'body',)
    readonly_fields = ('created',)


@admin.register(Reply)
class ReplyAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'letter', 'message',)
    readonly_fields = ('created', 'modified')


@admin.register(TriggerType)
class TriggerType(admin.ModelAdmin):
    list_display = ('id', 'name', 'human_name', 'desc',)


@admin.register(Trigger)
class Trigger(admin.ModelAdmin):
    list_display = ('id', 'hotel', 'type', 'reply')