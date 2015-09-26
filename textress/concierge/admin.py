from django.contrib import admin


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
    list_display = ('hotel', 'letter', 'message',)
    readonly_fields = ('created', 'modified')
