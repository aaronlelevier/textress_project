# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Hotel.city'
        db.delete_column('main_hotel', 'city')

        # Deleting field 'Hotel.line2'
        db.delete_column('main_hotel', 'line2')

        # Deleting field 'Hotel.state'
        db.delete_column('main_hotel', 'state')

        # Deleting field 'Hotel.line1'
        db.delete_column('main_hotel', 'line1')

        # Deleting field 'Hotel.zipcode'
        db.delete_column('main_hotel', 'zipcode')

        # Adding field 'Hotel.address_line1'
        db.add_column('main_hotel', 'address_line1',
                      self.gf('django.db.models.fields.CharField')(max_length=100, default=1),
                      keep_default=False)

        # Adding field 'Hotel.address_line2'
        db.add_column('main_hotel', 'address_line2',
                      self.gf('django.db.models.fields.CharField')(max_length=100, blank=True, default=''),
                      keep_default=False)

        # Adding field 'Hotel.address_city'
        db.add_column('main_hotel', 'address_city',
                      self.gf('django.db.models.fields.CharField')(max_length=100, default=1),
                      keep_default=False)

        # Adding field 'Hotel.address_state'
        db.add_column('main_hotel', 'address_state',
                      self.gf('django.db.models.fields.CharField')(max_length=25, default='Alabama'),
                      keep_default=False)

        # Adding field 'Hotel.address_zip'
        db.add_column('main_hotel', 'address_zip',
                      self.gf('django.db.models.fields.IntegerField')(max_length=5, default=1),
                      keep_default=False)


    def backwards(self, orm):
        # Adding field 'Hotel.city'
        db.add_column('main_hotel', 'city',
                      self.gf('django.db.models.fields.CharField')(max_length=100, default=1),
                      keep_default=False)

        # Adding field 'Hotel.line2'
        db.add_column('main_hotel', 'line2',
                      self.gf('django.db.models.fields.CharField')(max_length=100, blank=True, default=''),
                      keep_default=False)

        # Adding field 'Hotel.state'
        db.add_column('main_hotel', 'state',
                      self.gf('django.db.models.fields.CharField')(max_length=25, default='Alabama'),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Hotel.line1'
        raise RuntimeError("Cannot reverse this migration. 'Hotel.line1' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Hotel.line1'
        db.add_column('main_hotel', 'line1',
                      self.gf('django.db.models.fields.CharField')(max_length=100),
                      keep_default=False)


        # User chose to not deal with backwards NULL issues for 'Hotel.zipcode'
        raise RuntimeError("Cannot reverse this migration. 'Hotel.zipcode' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'Hotel.zipcode'
        db.add_column('main_hotel', 'zipcode',
                      self.gf('django.db.models.fields.IntegerField')(max_length=5),
                      keep_default=False)

        # Deleting field 'Hotel.address_line1'
        db.delete_column('main_hotel', 'address_line1')

        # Deleting field 'Hotel.address_line2'
        db.delete_column('main_hotel', 'address_line2')

        # Deleting field 'Hotel.address_city'
        db.delete_column('main_hotel', 'address_city')

        # Deleting field 'Hotel.address_state'
        db.delete_column('main_hotel', 'address_state')

        # Deleting field 'Hotel.address_zip'
        db.delete_column('main_hotel', 'address_zip')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'blank': 'True', 'symmetrical': 'False'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'related_name': "'user_set'", 'blank': 'True', 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'related_name': "'user_set'", 'blank': 'True', 'symmetrical': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30', 'unique': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'main.hotel': {
            'Meta': {'ordering': "('created',)", 'object_name': 'Hotel'},
            'account_sid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'address_city': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'address_line1': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'address_line2': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'address_state': ('django.db.models.fields.CharField', [], {'max_length': '25', 'default': "'Alabama'"}),
            'address_zip': ('django.db.models.fields.IntegerField', [], {'max_length': '5'}),
            'admin_id': ('django.db.models.fields.IntegerField', [], {'blank': 'True', 'null': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Customer']", 'blank': 'True', 'null': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hotel_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True', 'default': "''"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'phone_alt': ('django.db.models.fields.CharField', [], {'max_length': '12', 'blank': 'True'}),
            'phone_number_sid': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'rooms': ('django.db.models.fields.IntegerField', [], {'max_length': '5', 'blank': 'True', 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '125', 'blank': 'True'})
        },
        'main.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Hotel']", 'blank': 'True', 'null': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'primary_key': 'True', 'unique': 'True', 'related_name': "'profile'"})
        },
        'payment.customer': {
            'Meta': {'object_name': 'Customer'},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'default_card': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Subscription']"})
        },
        'payment.plan': {
            'Meta': {'object_name': 'Plan'},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'interval': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'price': ('django.db.models.fields.FloatField', [], {'blank': 'True', 'null': 'True'}),
            'price_per_extra': ('django.db.models.fields.FloatField', [], {}),
            'sms_per_month': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'payment.subscription': {
            'Meta': {'object_name': 'Subscription'},
            'created': ('django.db.models.fields.DateTimeField', [], {'blank': 'True', 'auto_now_add': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Plan']"})
        }
    }

    complete_apps = ['main']