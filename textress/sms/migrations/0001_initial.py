# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Text'
        db.create_table('sms_text', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('to', self.gf('django.db.models.fields.CharField')(max_length=12)),
            ('frm', self.gf('django.db.models.fields.CharField')(default='+17028324062', blank=True, max_length=12)),
            ('body', self.gf('django.db.models.fields.CharField')(blank=True, max_length=160)),
            ('sent', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('sms', ['Text'])

        # Adding model 'DemoCounter'
        db.create_table('sms_democounter', (
            ('day', self.gf('django.db.models.fields.DateField')(auto_now_add=True, primary_key=True)),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=1, blank=True)),
        ))
        db.send_create_signal('sms', ['DemoCounter'])


    def backwards(self, orm):
        # Deleting model 'Text'
        db.delete_table('sms_text')

        # Deleting model 'DemoCounter'
        db.delete_table('sms_democounter')


    models = {
        'sms.democounter': {
            'Meta': {'object_name': 'DemoCounter'},
            'count': ('django.db.models.fields.IntegerField', [], {'default': '1', 'blank': 'True'}),
            'day': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'primary_key': 'True'})
        },
        'sms.text': {
            'Meta': {'object_name': 'Text'},
            'body': ('django.db.models.fields.CharField', [], {'blank': 'True', 'max_length': '160'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'frm': ('django.db.models.fields.CharField', [], {'default': "'+17028324062'", 'blank': 'True', 'max_length': '12'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sent': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'to': ('django.db.models.fields.CharField', [], {'max_length': '12'})
        }
    }

    complete_apps = ['sms']