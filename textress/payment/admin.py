from django.contrib import admin

from .models import Customer, Card, Charge, Refund


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'created',)


class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'created',)


class ChargeAdmin(admin.ModelAdmin):
    list_display = ('id', 'created',)


class RefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'created',)


admin.site.register(Customer, CustomerAdmin)
admin.site.register(Card, CardAdmin)
admin.site.register(Charge, ChargeAdmin)
admin.site.register(Refund, RefundAdmin)
