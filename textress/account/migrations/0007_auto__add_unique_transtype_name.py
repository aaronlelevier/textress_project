# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding unique constraint on 'TransType', fields ['name']
        db.create_unique('account_transtype', ['name'])


    def backwards(self, orm):
        # Removing unique constraint on 'TransType', fields ['name']
        db.delete_unique('account_transtype', ['name'])


    models = {
        'account.acctcost': {
            'Meta': {'object_name': 'AcctCost'},
            'balance_min': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'hotel': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'acct_cost'", 'unique': 'True', 'to': "orm['main.Hotel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'init_amt': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'recharge_amt': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'})
        },
        'account.acctstmt': {
            'Meta': {'object_name': 'AcctStmt'},
            'balance': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'acct_stmt'", 'to': "orm['main.Hotel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'monthly_costs': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'default': '500.0'}),
            'total_sms': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'default': '0'}),
            'year': ('django.db.models.fields.IntegerField', [], {'blank': 'True'})
        },
        'account.accttrans': {
            'Meta': {'object_name': 'AcctTrans'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'credit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'debit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'acct_trans'", 'to': "orm['main.Hotel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insert_date': ('django.db.models.fields.DateField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'sms_used': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'default': '0', 'null': 'True'}),
            'trans_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.TransType']"})
        },
        'account.transtype': {
            'Meta': {'object_name': 'TransType', 'ordering': "['id']"},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'main.hotel': {
            'Meta': {'object_name': 'Hotel', 'ordering': "['-created']"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'address_city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'address_line1': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'address_line2': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '100'}),
            'address_state': ('django.db.models.fields.CharField', [], {'default': "'Alabama'", 'max_length': '25'}),
            'address_zip': ('django.db.models.fields.IntegerField', [], {'max_length': '5'}),
            'admin_id': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'unique': 'True', 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['payment.Customer']", 'null': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hotel_type': ('django.db.models.fields.CharField', [], {'blank': 'True', 'default': "''", 'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'rooms': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True', 'max_length': '5'}),
            'slug': ('django.db.models.fields.SlugField', [], {'blank': 'True', 'unique': 'True', 'max_length': '125'})
        },
        'payment.customer': {
            'Meta': {'object_name': 'Customer', 'ordering': "['-created']"},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'to': "orm['payment.Subscription']", 'null': 'True'})
        },
        'payment.plan': {
            'Meta': {'object_name': 'Plan', 'ordering': "['-created']"},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'interval': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '25'}),
            'price_per_extra': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'default': '0'}),
            'sms_per_month': ('django.db.models.fields.PositiveIntegerField', [], {'blank': 'True', 'default': '0'})
        },
        'payment.subscription': {
            'Meta': {'object_name': 'Subscription', 'ordering': "['-created']"},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Plan']"})
        }
    }

    complete_apps = ['account']