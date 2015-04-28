# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting model 'AccountCost'
        db.delete_table('account_accountcost')

        # Deleting model 'AccountStatement'
        db.delete_table('account_accountstatement')

        # Deleting model 'AccountTransactions'
        db.delete_table('account_accounttransactions')

        # Adding model 'AcctTrans'
        db.create_table('account_accttrans', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('hotel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Hotel'], related_name='acct_trans')),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
            ('monthly_fee', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('sms_used', self.gf('django.db.models.fields.IntegerField')(default=0, blank=True)),
        ))
        db.send_create_signal('account', ['AcctTrans'])

        # Adding model 'AcctCost'
        db.create_table('account_acctcost', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('hotel', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['main.Hotel'], related_name='acct_cost', unique=True)),
            ('monthly_fee', self.gf('django.db.models.fields.FloatField')(default=1000, blank=True)),
            ('per_sms_cost', self.gf('django.db.models.fields.FloatField')(default=1, blank=True)),
        ))
        db.send_create_signal('account', ['AcctCost'])

        # Adding model 'AcctStmt'
        db.create_table('account_acctstmt', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('hotel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Hotel'], related_name='acct_stmt')),
            ('total_sms', self.gf('django.db.models.fields.IntegerField')()),
            ('monthly_cost', self.gf('django.db.models.fields.FloatField')()),
            ('balance', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('account', ['AcctStmt'])


    def backwards(self, orm):
        # Adding model 'AccountCost'
        db.create_table('account_accountcost', (
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('hotel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Hotel'])),
            ('monthly_fee', self.gf('django.db.models.fields.FloatField')(blank=True, default=1000)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('per_sms_cost', self.gf('django.db.models.fields.FloatField')(blank=True, default=1)),
        ))
        db.send_create_signal('account', ['AccountCost'])

        # Adding model 'AccountStatement'
        db.create_table('account_accountstatement', (
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hotel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Hotel'])),
            ('created', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('balance', self.gf('django.db.models.fields.FloatField')()),
            ('total_sms', self.gf('django.db.models.fields.IntegerField')()),
            ('monthly_cost', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('account', ['AccountStatement'])

        # Adding model 'AccountTransactions'
        db.create_table('account_accounttransactions', (
            ('hidden', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('hotel', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['main.Hotel'])),
            ('sms_used', self.gf('django.db.models.fields.IntegerField')(blank=True, default=0)),
            ('monthly_fee', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(blank=True, auto_now_add=True)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('amount', self.gf('django.db.models.fields.FloatField')()),
        ))
        db.send_create_signal('account', ['AccountTransactions'])

        # Deleting model 'AcctTrans'
        db.delete_table('account_accttrans')

        # Deleting model 'AcctCost'
        db.delete_table('account_acctcost')

        # Deleting model 'AcctStmt'
        db.delete_table('account_acctstmt')


    models = {
        'account.acctcost': {
            'Meta': {'object_name': 'AcctCost'},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hotel': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['main.Hotel']", 'related_name': "'acct_cost'", 'unique': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'monthly_fee': ('django.db.models.fields.FloatField', [], {'default': '1000', 'blank': 'True'}),
            'per_sms_cost': ('django.db.models.fields.FloatField', [], {'default': '1', 'blank': 'True'})
        },
        'account.acctstmt': {
            'Meta': {'object_name': 'AcctStmt'},
            'balance': ('django.db.models.fields.FloatField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Hotel']", 'related_name': "'acct_stmt'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'monthly_cost': ('django.db.models.fields.FloatField', [], {}),
            'total_sms': ('django.db.models.fields.IntegerField', [], {})
        },
        'account.accttrans': {
            'Meta': {'object_name': 'AcctTrans'},
            'amount': ('django.db.models.fields.FloatField', [], {}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'hotel': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['main.Hotel']", 'related_name': "'acct_trans'"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'monthly_fee': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sms_used': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
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
            'customer': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Customer']", 'null': 'True', 'blank': 'True'}),
            'hidden': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'hotel_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'default': "''", 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100', 'unique': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '12'}),
            'rooms': ('django.db.models.fields.IntegerField', [], {'max_length': '5', 'null': 'True', 'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '125', 'blank': 'True', 'unique': 'True'})
        },
        'payment.customer': {
            'Meta': {'object_name': 'Customer', 'ordering': "['-created']"},
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'subscription': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['payment.Subscription']", 'null': 'True', 'blank': 'True'})
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