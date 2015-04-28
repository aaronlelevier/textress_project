# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AccountCost'
        db.create_table('account_accountcost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hotel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Hotel'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('monthly_fee', self.gf('django.db.models.fields.FloatField')(default=1000, blank=True)),
            ('per_sms_cost', self.gf('django.db.models.fields.FloatField')(default=1, blank=True)),
        ))
        db.send_create_signal('account', ['AccountCost'])

        # Adding model 'AccountStatement'
        db.create_table('account_accountstatement', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hotel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Hotel'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('total_sms', self.gf('django.db.models.fields.IntegerField')()),
            ('monthly_cost', self.gf('django.db.models.fields.FloatField')()),
            ('balance', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('account', ['AccountStatement'])

        # Adding model 'AccountTransactions'
        db.create_table('account_accounttransactions', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hotel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Hotel'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('monthly_fee', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sms_used', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('account', ['AccountTransactions'])


    def backwards(self, orm):
        # Deleting model 'AccountCost'
        db.delete_table('account_accountcost')

        # Deleting model 'AccountStatement'
        db.delete_table('account_accountstatement')

        # Deleting model 'AccountTransactions'
        db.delete_table('account_accounttransactions')


    models = {
        'account.accountcost': {
            'Meta': {'object_name': 'AccountCost'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Hotel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'monthly_fee': ('django.db.models.fields.FloatField', [], {'default': '1000', 'blank': 'True'}),
            'per_sms_cost': ('django.db.models.fields.FloatField', [], {'default': '1', 'blank': 'True'})
        },
        'account.accountstatement': {
            'Meta': {'object_name': 'AccountStatement'},
            'balance': ('django.db.models.fields.FloatField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Hotel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monthly_cost': ('django.db.models.fields.FloatField', [], {}),
            'total_sms': ('django.db.models.fields.IntegerField', [], {})
        },
        'account.accounttransactions': {
            'Meta': {'object_name': 'AccountTransactions'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Hotel']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'monthly_fee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sms_used': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        },
        'main.hotel': {
            'Meta': {'ordering': "('created',)", 'object_name': 'Hotel'},
            'account_sid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'admin_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'city': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'to': "orm['payment.Customer']", 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hotel_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'line1': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'line2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'phone_alt': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'phone_number_sid': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'rooms': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'max_length': '5', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '125', 'blank': 'True'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '25', 'default': "'Alabama'"}),
            'stripe_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'zipcode': ('django.db.models.fields.IntegerField', [], {'max_length': '5'})
        },
        'payment.customer': {
            'Meta': {'object_name': 'Customer'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'default_card': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Subscription']"})
        },
        'payment.plan': {
            'Meta': {'object_name': 'Plan'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'interval': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'price': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'price_per_extra': ('django.db.models.fields.FloatField', [], {}),
            'sms_per_month': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'payment.subscription': {
            'Meta': {'object_name': 'Subscription'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Plan']"})
        }
    }

    complete_apps = ['account']