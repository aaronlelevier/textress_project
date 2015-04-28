# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Card.last4'
        db.delete_column('payment_card', 'last4')

        # Deleting field 'Card.exp_year'
        db.delete_column('payment_card', 'exp_year')

        # Deleting field 'Card.brand'
        db.delete_column('payment_card', 'brand')

        # Deleting field 'Card.exp_month'
        db.delete_column('payment_card', 'exp_month')

        # Deleting field 'Card.expires'
        db.delete_column('payment_card', 'expires')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'Card.last4'
        raise RuntimeError("Cannot reverse this migration. 'Card.last4' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Card.last4'
        db.add_column('payment_card', 'last4',
                      self.gf('django.db.models.fields.PositiveIntegerField')(max_length=4),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Card.exp_year'
        raise RuntimeError("Cannot reverse this migration. 'Card.exp_year' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Card.exp_year'
        db.add_column('payment_card', 'exp_year',
                      self.gf('django.db.models.fields.PositiveIntegerField')(max_length=4),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Card.brand'
        raise RuntimeError("Cannot reverse this migration. 'Card.brand' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Card.brand'
        db.add_column('payment_card', 'brand',
                      self.gf('django.db.models.fields.CharField')(max_length=25),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Card.exp_month'
        raise RuntimeError("Cannot reverse this migration. 'Card.exp_month' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Card.exp_month'
        db.add_column('payment_card', 'exp_month',
                      self.gf('django.db.models.fields.PositiveIntegerField')(max_length=2),
                      keep_default=False)

        # Adding field 'Card.expires'
        db.add_column('payment_card', 'expires',
                      self.gf('django.db.models.fields.CharField')(max_length=10, default='', blank=True),
                      keep_default=False)


    models = {
        'payment.card': {
            'Meta': {'object_name': 'Card', 'ordering': "['-created']"},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'cards'", 'to': "orm['payment.Customer']"}),
            'default': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'max_length': '6', 'unique': 'True', 'blank': 'True'})
        },
        'payment.charge': {
            'Meta': {'object_name': 'Charge', 'ordering': "['-created']"},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'card': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Card']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Customer']"}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'null': 'True'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'max_length': '6', 'unique': 'True', 'blank': 'True'})
        },
        'payment.customer': {
            'Meta': {'object_name': 'Customer', 'ordering': "['-created']"},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'to': "orm['payment.Subscription']"})
        },
        'payment.plan': {
            'Meta': {'object_name': 'Plan', 'ordering': "['-created']"},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'interval': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25', 'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'null': 'True'}),
            'price_per_extra': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'sms_per_month': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0', 'blank': 'True'})
        },
        'payment.refund': {
            'Meta': {'object_name': 'Refund', 'ordering': "['-created']"},
            'charge': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'refunds'", 'to': "orm['payment.Charge']"}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'price': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'null': 'True'}),
            'short_pk': ('django.db.models.fields.CharField', [], {'max_length': '6', 'unique': 'True', 'blank': 'True'})
        },
        'payment.subscription': {
            'Meta': {'object_name': 'Subscription', 'ordering': "['-created']"},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Plan']"})
        }
    }

    complete_apps = ['payment']