# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'AcctTrans.credit_debit'
        db.add_column('account_accttrans', 'credit_debit',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'AcctTrans.credit_debit'
        db.delete_column('account_accttrans', 'credit_debit')


    models = {
        'account.acctcost': {
            'Meta': {'object_name': 'AcctCost'},
            'balance_min': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'hotel': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Hotel']", 'unique': 'True', 'related_name': "'acct_cost'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'init_amt': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'recharge_amt': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'})
        },
        'account.acctstmt': {
            'Meta': {'object_name': 'AcctStmt'},
            'balance': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Hotel']", 'related_name': "'acct_stmt'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'monthly_costs': ('django.db.models.fields.FloatField', [], {'default': '5.0', 'blank': 'True'}),
            'total_sms': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'blank': 'True'})
        },
        'account.accttrans': {
            'Meta': {'object_name': 'AcctTrans'},
            'amount': ('django.db.models.fields.FloatField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'credit_debit': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Hotel']", 'related_name': "'acct_trans'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insert_date': ('django.db.models.fields.DateField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'sms_used': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True', 'null': 'True'}),
            'trans_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.TransType']"})
        },
        'account.transtype': {
            'Meta': {'ordering': "['id']", 'object_name': 'TransType'},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'main.hotel': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Hotel'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'address_city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'address_line1': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'address_line2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_state': ('django.db.models.fields.CharField', [], {'max_length': '25', 'default': "'Alabama'"}),
            'address_zip': ('django.db.models.fields.IntegerField', [], {'max_length': '5'}),
            'admin_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'blank': 'True', 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Customer']", 'blank': 'True', 'null': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hotel_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'rooms': ('django.db.models.fields.IntegerField', [], {'max_length': '5', 'blank': 'True', 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '125', 'unique': 'True', 'blank': 'True'})
        },
        'payment.customer': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Customer'},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Subscription']", 'blank': 'True', 'null': 'True'})
        },
        'payment.plan': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Plan'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'interval': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'price_per_extra': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'sms_per_month': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'})
        },
        'payment.subscription': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Subscription'},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Plan']"})
        }
    }

    complete_apps = ['account']