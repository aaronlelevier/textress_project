# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Card.exp_month'
        db.add_column('payment_card', 'exp_month',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=12, max_length=2),
                      keep_default=False)

        # Adding field 'Card.exp_year'
        db.add_column('payment_card', 'exp_year',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=2018, max_length=4),
                      keep_default=False)

        # Adding field 'Card.expires'
        db.add_column('payment_card', 'expires',
                      self.gf('django.db.models.fields.CharField')(blank=True, default='', max_length=10),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Card.exp_month'
        db.delete_column('payment_card', 'exp_month')

        # Deleting field 'Card.exp_year'
        db.delete_column('payment_card', 'exp_year')

        # Deleting field 'Card.expires'
        db.delete_column('payment_card', 'expires')


    models = {
        'payment.card': {
            'Meta': {'object_name': 'Card', 'ordering': "['-created']"},
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Customer']", 'related_name': "'cards'"}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'exp_month': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '2'}),
            'exp_year': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '4'}),
            'expires': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '10'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'last4': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '4'}),
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