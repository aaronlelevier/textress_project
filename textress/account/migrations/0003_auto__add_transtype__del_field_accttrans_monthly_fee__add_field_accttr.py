# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TransType'
        db.create_table('account_transtype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('desc', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal('account', ['TransType'])

        # Deleting field 'AcctTrans.monthly_fee'
        db.delete_column('account_accttrans', 'monthly_fee')

        # Adding field 'AcctTrans.trans_type'
        db.add_column('account_accttrans', 'trans_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['account.TransType'], default=1),
                      keep_default=False)

        # Adding field 'AcctTrans.insert_date'
        db.add_column('account_accttrans', 'insert_date',
                      self.gf('django.db.models.fields.DateField')(auto_now_add=True, default=datetime.datetime(2014, 12, 26, 0, 0), blank=True),
                      keep_default=False)


        # Changing field 'AcctTrans.sms_used'
        db.alter_column('account_accttrans', 'sms_used', self.gf('django.db.models.fields.IntegerField')(null=True))
        # Deleting field 'AcctStmt.monthly_cost'
        db.delete_column('account_acctstmt', 'monthly_cost')

        # Adding field 'AcctStmt.year'
        db.add_column('account_acctstmt', 'year',
                      self.gf('django.db.models.fields.IntegerField')(default=2014, blank=True),
                      keep_default=False)

        # Adding field 'AcctStmt.month'
        db.add_column('account_acctstmt', 'month',
                      self.gf('django.db.models.fields.IntegerField')(default=12, blank=True),
                      keep_default=False)

        # Adding field 'AcctStmt.monthly_costs'
        db.add_column('account_acctstmt', 'monthly_costs',
                      self.gf('django.db.models.fields.FloatField')(default=5.0, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'TransType'
        db.delete_table('account_transtype')

        # Adding field 'AcctTrans.monthly_fee'
        db.add_column('account_accttrans', 'monthly_fee',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Deleting field 'AcctTrans.trans_type'
        db.delete_column('account_accttrans', 'trans_type_id')

        # Deleting field 'AcctTrans.insert_date'
        db.delete_column('account_accttrans', 'insert_date')


        # Changing field 'AcctTrans.sms_used'
        db.alter_column('account_accttrans', 'sms_used', self.gf('django.db.models.fields.IntegerField')())
        # Adding field 'AcctStmt.monthly_cost'
        db.add_column('account_acctstmt', 'monthly_cost',
                      self.gf('django.db.models.fields.FloatField')(default=5.0),
                      keep_default=False)

        # Deleting field 'AcctStmt.year'
        db.delete_column('account_acctstmt', 'year')

        # Deleting field 'AcctStmt.month'
        db.delete_column('account_acctstmt', 'month')

        # Deleting field 'AcctStmt.monthly_costs'
        db.delete_column('account_acctstmt', 'monthly_costs')


    models = {
        'account.acctcost': {
            'Meta': {'object_name': 'AcctCost'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hotel': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Hotel']", 'unique': 'True', 'related_name': "'acct_cost'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'monthly_fee': ('django.db.models.fields.FloatField', [], {'default': '5.0', 'blank': 'True'}),
            'per_sms_cost': ('django.db.models.fields.FloatField', [], {'default': '0.05', 'blank': 'True'})
        },
        'account.acctstmt': {
            'Meta': {'object_name': 'AcctStmt'},
            'balance': ('django.db.models.fields.FloatField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Hotel']", 'related_name': "'acct_stmt'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'month': ('django.db.models.fields.IntegerField', [], {'blank': 'True'}),
            'monthly_costs': ('django.db.models.fields.FloatField', [], {'default': '5.0', 'blank': 'True'}),
            'total_sms': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'blank': 'True'})
        },
        'account.accttrans': {
            'Meta': {'object_name': 'AcctTrans'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Hotel']", 'related_name': "'acct_trans'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insert_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'sms_used': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'default': '0', 'blank': 'True'}),
            'trans_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['account.TransType']"})
        },
        'account.transtype': {
            'Meta': {'object_name': 'TransType', 'ordering': "['name']"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'desc': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'main.hotel': {
            'Meta': {'object_name': 'Hotel', 'ordering': "['-created']"},
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
            'hotel_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'rooms': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'max_length': '5', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '125', 'blank': 'True', 'unique': 'True'})
        },
        'payment.customer': {
            'Meta': {'object_name': 'Customer', 'ordering': "['-created']"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'null': 'True', 'blank': 'True', 'to': "orm['payment.Subscription']"})
        },
        'payment.plan': {
            'Meta': {'object_name': 'Plan', 'ordering': "['-created']"},
            'amount': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '5'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'interval': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'price': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'price_per_extra': ('django.db.models.fields.FloatField', [], {}),
            'sms_per_month': ('django.db.models.fields.PositiveIntegerField', [], {})
        },
        'payment.subscription': {
            'Meta': {'object_name': 'Subscription', 'ordering': "['-created']"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'plan': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Plan']"})
        }
    }

    complete_apps = ['account']