# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Card'
        db.create_table('payment_card', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now=True)),
            ('id', self.gf('django.db.models.fields.CharField')(primary_key=True, max_length=100)),
            ('customer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payment.Customer'], related_name='cards')),
            ('brand', self.gf('django.db.models.fields.CharField')(blank=True, max_length=25)),
            ('last4', self.gf('django.db.models.fields.PositiveIntegerField')(blank=True, max_length=4)),
            ('default', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('payment', ['Card'])

        # Adding model 'Charge'
        db.create_table('payment_charge', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now=True)),
            ('id', self.gf('django.db.models.fields.CharField')(primary_key=True, max_length=100)),
            ('card', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payment.Card'], related_name='charges')),
        ))
        db.send_create_signal('payment', ['Charge'])

        # Adding model 'Refund'
        db.create_table('payment_refund', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now=True)),
            ('id', self.gf('django.db.models.fields.CharField')(primary_key=True, max_length=100)),
            ('charge', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payment.Charge'], related_name='refunds')),
        ))
        db.send_create_signal('payment', ['Refund'])


    def backwards(self, orm):
        # Deleting model 'Card'
        db.delete_table('payment_card')

        # Deleting model 'Charge'
        db.delete_table('payment_charge')

        # Deleting model 'Refund'
        db.delete_table('payment_refund')


    models = {
        'payment.card': {
            'Meta': {'object_name': 'Card', 'ordering': "['-created']"},
            'brand': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '25'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Customer']", 'related_name': "'cards'"}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'last4': ('django.db.models.fields.PositiveIntegerField', [], {'blank': 'True', 'max_length': '4'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'})
        },
        'payment.charge': {
            'Meta': {'object_name': 'Charge', 'ordering': "['-created']"},
            'card': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Card']", 'related_name': "'charges'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'})
        },
        'payment.customer': {
            'Meta': {'object_name': 'Customer', 'ordering': "['-created']"},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'blank': 'True', 'max_length': '75'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['payment.Subscription']"})
        },
        'payment.plan': {
            'Meta': {'object_name': 'Plan', 'ordering': "['-created']"},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'interval': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'price': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'null': 'True'}),
            'price_per_extra': ('django.db.models.fields.FloatField', [], {}),
            'sms_per_month': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'payment.refund': {
            'Meta': {'object_name': 'Refund', 'ordering': "['-created']"},
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Charge']", 'related_name': "'refunds'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'})
        },
        'payment.subscription': {
            'Meta': {'object_name': 'Subscription', 'ordering': "['-created']"},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Plan']"})
        }
    }

    complete_apps = ['payment']