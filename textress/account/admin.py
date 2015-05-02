from django.contrib import admin
from django.db import models
from django.forms.widgets import TextInput

from account.models import AcctCost, AcctStmt, AcctTrans, TransType, Pricing


@admin.register(TransType)
class TransTypeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'desc',)
    readonly_fields = ('created', 'modified',)
    formfield_overrides = {
            models.CharField: {'widget': TextInput(attrs={'size':'100'})},
        }


@admin.register(AcctCost)
class AcctCostAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'init_amt', 'balance_min', 'recharge_amt',)
    readonly_fields = ('created', 'modified',)


@admin.register(AcctStmt)
class AcctStmtAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'year', 'month', 'monthly_costs', 'balance',)
    readonly_fields = ('created', 'modified',)


@admin.register(AcctTrans)
class AcctTransAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'created', 'insert_date', 'trans_type',)
    readonly_fields = ('created', 'modified',)


@admin.register(Pricing)
class PricingAdmin(admin.ModelAdmin):
    list_display = ('tier', 'tier_name', 'desc', 'price', 'start', 'end',)
    readonly_fields = ('created', 'modified',)