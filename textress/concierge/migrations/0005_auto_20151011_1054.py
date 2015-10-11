# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
        ('concierge', '0004_auto_20151007_0616'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trigger',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('active', models.BooleanField(default=False)),
                ('hotel', models.ForeignKey(to='main.Hotel')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TriggerType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('hidden', models.BooleanField(default=False, verbose_name='Hide')),
                ('name', models.CharField(unique=True, max_length=100)),
                ('desc', models.CharField(help_text=b"Use to store information about what each Trigger type will actually do. i.e. 'check_in' will be used to send welcome messages.", max_length=254, blank=True)),
                ('reply', models.ForeignKey(to='concierge.Reply')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='trigger',
            name='type',
            field=models.ForeignKey(to='concierge.TriggerType'),
        ),
    ]
