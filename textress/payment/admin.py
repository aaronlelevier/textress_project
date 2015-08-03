from django.contrib import admin

from payment.models import Customer, CardImage, Card, Charge, Refund


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('id', 'created',)


@admin.register(CardImage)
class CardAdmin(admin.ModelAdmin):
    pass
    

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'created',)


@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display = ('id', 'created',)


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ('id', 'created',)
