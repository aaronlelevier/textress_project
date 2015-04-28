# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Plan'
        db.create_table('payment_plan', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
            ('amount', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('interval', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=5)),
            ('sms_per_month', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('price_per_extra', self.gf('django.db.models.fields.FloatField')()),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('price', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
        ))
        db.send_create_signal('payment', ['Plan'])

        # Adding model 'Subscription'
        db.create_table('payment_subscription', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
            ('plan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payment.Plan'])),
        ))
        db.send_create_signal('payment', ['Subscription'])

        # Adding model 'Customer'
        db.create_table('payment_customer', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
            ('subscription', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payment.Subscription'])),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('default_card', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal('payment', ['Customer'])

        # Adding model 'Card'
        db.create_table('payment_card', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payment.Customer'], related_name='cards')),
        ))
        db.send_create_signal('payment', ['Card'])

        # Adding model 'Charge'
        db.create_table('payment_charge', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
            ('card', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payment.Card'])),
        ))
        db.send_create_signal('payment', ['Charge'])

        # Adding model 'Refund'
        db.create_table('payment_refund', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('id', self.gf('django.db.models.fields.CharField')(max_length=50, primary_key=True)),
            ('charge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payment.Charge'], related_name='refunds')),
        ))
        db.send_create_signal('payment', ['Refund'])


    def backwards(self, orm):
        # Deleting model 'Plan'
        db.delete_table('payment_plan')

        # Deleting model 'Subscription'
        db.delete_table('payment_subscription')

        # Deleting model 'Customer'
        db.delete_table('payment_customer')

        # Deleting model 'Card'
        db.delete_table('payment_card')

        # Deleting model 'Charge'
        db.delete_table('payment_charge')

        # Deleting model 'Refund'
        db.delete_table('payment_refund')


    models = {
        'payment.card': {
            'Meta': {'object_name': 'Card'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Customer']", 'related_name': "'cards'"}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'payment.charge': {
            'Meta': {'object_name': 'Charge'},
            'card': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Card']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
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
        'payment.refund': {
            'Meta': {'object_name': 'Refund'},
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Charge']", 'related_name': "'refunds'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'payment.subscription': {
            'Meta': {'object_name': 'Subscription'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Plan']"})
        }
    }

    complete_apps = ['payment']