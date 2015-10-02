# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='accttrans',
            name='hotel',
            field=models.ForeignKey(related_name='acct_trans', to='main.Hotel'),
        ),
        migrations.AddField(
            model_name='accttrans',
            name='trans_type',
            field=models.ForeignKey(to='account.TransType'),
        ),
        migrations.AddField(
            model_name='acctstmt',
            name='hotel',
            field=models.ForeignKey(related_name='acct_stmt', to='main.Hotel'),
        ),
        migrations.AddField(
            model_name='acctcost',
            name='hotel',
            field=models.OneToOneField(related_name='acct_cost', to='main.Hotel'),
        ),
    ]
