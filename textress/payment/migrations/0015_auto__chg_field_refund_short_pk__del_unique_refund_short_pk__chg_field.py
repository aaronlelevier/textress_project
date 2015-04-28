# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Charge', fields ['short_pk']
        db.delete_unique('payment_charge', ['short_pk'])

        # Removing unique constraint on 'Card', fields ['short_pk']
        db.delete_unique('payment_card', ['short_pk'])

        # Removing unique constraint on 'Refund', fields ['short_pk']
        db.delete_unique('payment_refund', ['short_pk'])


        # Changing field 'Refund.short_pk'
        db.alter_column('payment_refund', 'short_pk', self.gf('django.db.models.fields.CharField')(max_length=10))

        # Changing field 'Card.short_pk'
        db.alter_column('payment_card', 'short_pk', self.gf('django.db.models.fields.CharField')(max_length=10))

        # Changing field 'Charge.short_pk'
        db.alter_column('payment_charge', 'short_pk', self.gf('django.db.models.fields.CharField')(max_length=10))
        # Adding field 'Customer.short_pk'
        db.add_column('payment_customer', 'short_pk',
                      self.gf('django.db.models.fields.CharField')(max_length=10, default='', blank=True),
                      keep_default=False)

        # Adding field 'Subscription.short_pk'
        db.add_column('payment_subscription', 'short_pk',
                      self.gf('django.db.models.fields.CharField')(max_length=10, default='', blank=True),
                      keep_default=False)

        # Adding field 'Plan.short_pk'
        db.add_column('payment_plan', 'short_pk',
                      self.gf('django.db.models.fields.CharField')(max_length=10, default='', blank=True),
                      keep_default=False)


    def backwards(self, orm):

        # Changing field 'Refund.short_pk'
        db.alter_column('payment_refund', 'short_pk', self.gf('django.db.models.fields.CharField')(max_length=6, unique=True))
        # Adding unique constraint on 'Refund', fields ['short_pk']
        db.create_unique('payment_refund', ['short_pk'])


        # Changing field 'Card.short_pk'
        db.alter_column('payment_card', 'short_pk', self.gf('django.db.models.fields.CharField')(max_length=6, unique=True))
        # Adding unique constraint on 'Card', fields ['short_pk']
        db.create_unique('payment_card', ['short_pk'])


        # Changing field 'Charge.short_pk'
        db.alter_column('payment_charge', 'short_pk', self.gf('django.db.models.fields.CharField')(max_length=6, unique=True))
        # Adding unique constraint on 'Charge', fields ['short_pk']
        db.create_unique('payment_charge', ['short_pk'])

        # Deleting field 'Customer.short_pk'
        db.delete_column('payment_customer', 'short_pk')

        # Deleting field 'Subscription.short_pk'
        db.delete_column('payment_subscription', 'short_pk')

        # Deleting field 'Plan.short_pk'
        db.delete_column('payment_plan', 'short_pk')


    models = {
        'payment.card': {
            'Meta': {'object_name': 'Card', 'ordering': "['-created']"},
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cards'", 'to': "orm['payment.Customer']"}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'exp_month': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '2'}),
            'exp_year': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '4'}),
            'expires': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'last4': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '4'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'payment.charge': {
            'Meta': {'object_name': 'Charge', 'ordering': "['-created']"},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'card': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Card']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Customer']"}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'payment.customer': {
            'Meta': {'object_name': 'Customer', 'ordering': "['-created']"},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'null': 'True', 'to': "orm['payment.Subscription']"})
        },
        'payment.plan': {
            'Meta': {'object_name': 'Plan', 'ordering': "['-created']"},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'interval': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'price_per_extra': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'default': '0'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'}),
            'sms_per_month': ('django.db.models.fields.PositiveIntegerField', [], {'blank': 'True', 'default': '0'})
        },
        'payment.refund': {
            'Meta': {'object_name': 'Refund', 'ordering': "['-created']"},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'refunds'", 'to': "orm['payment.Charge']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        },
        'payment.subscription': {
            'Meta': {'object_name': 'Subscription', 'ordering': "['-created']"},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Plan']"}),
            'short_pk': ('django.db.models.fields.CharField', [], {'max_length': '10', 'blank': 'True'})
        }
    }

    complete_apps = ['payment']