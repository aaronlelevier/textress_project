# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'AcctCost.per_sms'
        db.add_column('account_acctcost', 'per_sms',
                      self.gf('django.db.models.fields.FloatField')(default=5.5, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'AcctCost.per_sms'
        db.delete_column('account_acctcost', 'per_sms')


    models = {
        'account.acctcost': {
            'Meta': {'object_name': 'AcctCost'},
            'balance_min': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hotel': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'acct_cost'", 'to': "orm['main.Hotel']", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'init_amt': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'per_sms': ('django.db.models.fields.FloatField', [], {'default': '5.5', 'blank': 'True'}),
            'recharge_amt': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1000'})
        },
        'account.acctstmt': {
            'Meta': {'object_name': 'AcctStmt'},
            'balance': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'acct_stmt'", 'to': "orm['main.Hotel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'monthly_costs': ('django.db.models.fields.FloatField', [], {'default': '500.0', 'blank': 'True'}),
            'total_sms': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'blank': 'True'})
        },
        'account.accttrans': {
            'Meta': {'object_name': 'AcctTrans'},
            'amount': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'debit': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'acct_trans'", 'to': "orm['main.Hotel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insert_date': ('django.db.models.fields.DateField', [], {'blank': 'True', 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'sms_used': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True', 'null': 'True'}),
            'trans_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.TransType']"})
        },
        'account.transtype': {
            'Meta': {'ordering': "['id']", 'object_name': 'TransType'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'unique': 'True'})
        },
        'main.hotel': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Hotel'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'address_city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'address_line1': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'address_line2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_phone': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'address_state': ('django.db.models.fields.CharField', [], {'max_length': '25', 'default': "'Alabama'"}),
            'address_zip': ('django.db.models.fields.IntegerField', [], {'max_length': '5'}),
            'admin_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'blank': 'True', 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Customer']", 'blank': 'True', 'null': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hotel_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True'}),
            'rooms': ('django.db.models.fields.IntegerField', [], {'max_length': '5', 'blank': 'True', 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '125', 'unique': 'True', 'blank': 'True'}),
            'twilio_auth_token': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'twilio_phone_number': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'twilio_sid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'payment.customer': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Customer'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        }
    }

    complete_apps = ['account']