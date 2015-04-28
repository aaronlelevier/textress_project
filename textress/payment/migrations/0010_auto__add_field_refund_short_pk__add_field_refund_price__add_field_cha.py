# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Refund.short_pk'
        db.add_column('payment_refund', 'short_pk',
                      self.gf('django.db.models.fields.CharField')(unique=True, default='', max_length=6, blank=True),
                      keep_default=False)

        # Adding field 'Refund.price'
        db.add_column('payment_refund', 'price',
                      self.gf('django.db.models.fields.FloatField')(blank=True, null=True),
                      keep_default=False)

        # Adding field 'Charge.customer'
        db.add_column('payment_charge', 'customer',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['payment.Customer'], default='cus_5KHaHvvK6hEF5Y'),
                      keep_default=False)

        # Adding field 'Charge.amount'
        db.add_column('payment_charge', 'amount',
                      self.gf('django.db.models.fields.PositiveIntegerField')(default=1000),
                      keep_default=False)

        # Adding field 'Charge.short_pk'
        db.add_column('payment_charge', 'short_pk',
                      self.gf('django.db.models.fields.CharField')(unique=True, default='', max_length=6, blank=True),
                      keep_default=False)

        # Adding field 'Charge.price'
        db.add_column('payment_charge', 'price',
                      self.gf('django.db.models.fields.FloatField')(blank=True, null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Refund.short_pk'
        db.delete_column('payment_refund', 'short_pk')

        # Deleting field 'Refund.price'
        db.delete_column('payment_refund', 'price')

        # Deleting field 'Charge.customer'
        db.delete_column('payment_charge', 'customer_id')

        # Deleting field 'Charge.amount'
        db.delete_column('payment_charge', 'amount')

        # Deleting field 'Charge.short_pk'
        db.delete_column('payment_charge', 'short_pk')

        # Deleting field 'Charge.price'
        db.delete_column('payment_charge', 'price')


    models = {
        'payment.card': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Card'},
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Customer']", 'related_name': "'cards'"}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'exp_month': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '2'}),
            'exp_year': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '4'}),
            'expires': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'last4': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '4'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '6', 'blank': 'True'})
        },
        'payment.charge': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Charge'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'card': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Card']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Customer']"}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'null': 'True'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '6', 'blank': 'True'})
        },
        'payment.customer': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Customer'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Subscription']", 'blank': 'True', 'null': 'True'})
        },
        'payment.plan': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Plan'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'interval': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'null': 'True'}),
            'price_per_extra': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'sms_per_month': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'})
        },
        'payment.refund': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Refund'},
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Charge']", 'related_name': "'refunds'"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'null': 'True'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '6', 'blank': 'True'})
        },
        'payment.subscription': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Subscription'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '100'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Plan']"})
        }
    }

    complete_apps = ['payment']