# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'Plan'
        db.delete_table('payment_plan')

        # Deleting model 'Subscription'
        db.delete_table('payment_subscription')

        # Deleting field 'Customer.subscription'
        db.delete_column('payment_customer', 'subscription_id')


    def backwards(self, orm):
        # Adding model 'Plan'
        db.create_table('payment_plan', (
            ('interval', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('sms_per_month', self.gf('django.db.models.fields.PositiveIntegerField')(default=0, blank=True)),
            ('amount', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('price_per_extra', self.gf('django.db.models.fields.FloatField')(default=0, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('short_pk', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
        ))
        db.send_create_signal('payment', ['Plan'])

        # Adding model 'Subscription'
        db.create_table('payment_subscription', (
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=100, primary_key=True)),
            ('plan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payment.Plan'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('short_pk', self.gf('django.db.models.fields.CharField')(max_length=10, blank=True)),
        ))
        db.send_create_signal('payment', ['Subscription'])

        # Adding field 'Customer.subscription'
        db.add_column('payment_customer', 'subscription',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payment.Subscription'], null=True, blank=True),
                      keep_default=False)


    models = {
        'payment.card': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Card'},
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cards'", 'to': "orm['payment.Customer']"}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'exp_month': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '2'}),
            'exp_year': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '4'}),
            'expires': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'last4': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '4'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'payment.charge': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Charge'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'card': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Card']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Customer']"}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'payment.customer': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Customer'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'payment.refund': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Refund'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'refunds'", 'to': "orm['payment.Charge']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        }
    }

    complete_apps = ['payment']