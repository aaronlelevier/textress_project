# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'PhoneNumber'
        db.create_table('sms_phonenumber', (
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('sid', self.gf('django.db.models.fields.CharField')(primary_key=True, max_length=50)),
            ('hotel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Hotel'])),
            ('phone_number', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('friendly_name', self.gf('django.db.models.fields.CharField')(max_length=14)),
            ('is_primary', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('sms', ['PhoneNumber'])


    def backwards(self, orm):
        # Deleting model 'PhoneNumber'
        db.delete_table('sms_phonenumber')


    models = {
        'main.hotel': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Hotel'},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'address_city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'address_line1': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'address_line2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_state': ('django.db.models.fields.CharField', [], {'max_length': '25', 'default': "'Alabama'"}),
            'address_zip': ('django.db.models.fields.IntegerField', [], {'max_length': '5'}),
            'admin_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True', 'unique': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'to': "orm['payment.Customer']"}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hotel_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True', 'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'phone_number_sid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'rooms': ('django.db.models.fields.IntegerField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '125', 'blank': 'True', 'unique': 'True'}),
            'subaccount_sid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'})
        },
        'payment.customer': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Customer'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '50'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'to': "orm['payment.Subscription']"})
        },
        'payment.plan': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Plan'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '50'}),
            'interval': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'price': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'price_per_extra': ('django.db.models.fields.FloatField', [], {}),
            'sms_per_month': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'payment.subscription': {
            'Meta': {'ordering': "['-created']", 'object_name': 'Subscription'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '50'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Plan']"})
        },
        'sms.democounter': {
            'Meta': {'object_name': 'DemoCounter'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '1', 'blank': 'True'}),
            'day': ('django.db.models.fields.DateField', [], {'primary_key': 'True', 'auto_now_add': 'True'})
        },
        'sms.phonenumber': {
            'Meta': {'ordering': "['-created']", 'object_name': 'PhoneNumber'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'friendly_name': ('django.db.models.fields.CharField', [], {'max_length': '14'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Hotel']"}),
            'is_primary': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'phone_number': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'sid': ('django.db.models.fields.CharField', [], {'primary_key': 'True', 'max_length': '50'})
        },
        'sms.text': {
            'Meta': {'object_name': 'Text'},
            'body': ('django.db.models.fields.CharField', [], {'max_length': '160', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'frm': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True', 'default': "'+17754194000'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'to': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        }
    }

    complete_apps = ['sms']