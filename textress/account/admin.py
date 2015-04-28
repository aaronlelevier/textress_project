from django.contrib import admin
from django.db import models
from django.forms.widgets import TextInput

from .models import AcctCost, AcctStmt, AcctTrans, TransType, Pricing


class TransTypeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'desc',)
    readonly_fields = ('created', 'modified',)
    formfield_overrides = {
            models.CharField: {'widget': TextInput(attrs={'size':'100'})},
        }

class AcctCostAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'init_amt', 'balance_min', 'recharge_amt',)
    readonly_fields = ('created', 'modified',)


class AcctStmtAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'year', 'month', 'monthly_costs', 'balance',)
    readonly_fields = ('created', 'modified',)


class AcctTransAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'created', 'insert_date', 'trans_type',)
    readonly_fields = ('created', 'modified',)


class PricingAdmin(admin.ModelAdmin):
    list_display = ('tier', 'tier_name', 'desc', 'price', 'start', 'end',)
    readonly_fields = ('created', 'modified',)


admin.site.register(TransType, TransTypeAdmin)
admin.site.register(AcctCost, AcctCostAdmin)
admin.site.register(AcctStmt, AcctStmtAdmin)
admin.site.register(AcctTrans, AcctTransAdmin)
admin.site.register(Pricing, PricingAdmin)