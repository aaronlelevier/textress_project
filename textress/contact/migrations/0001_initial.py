# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('email', models.EmailField(max_length=100, verbose_name='Email')),
                ('subject', models.CharField(max_length=255, verbose_name='Subject', blank=True)),
                ('message', models.TextField(max_length=2000, verbose_name='Message')),
            ],
        ),
        migrations.CreateModel(
            name='QA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('question', models.CharField(max_length=255, verbose_name='Question', blank=True)),
                ('answer', models.TextField(max_length=1000, verbose_name='Answer', blank=True)),
                ('order', models.IntegerField(default=0, help_text=b"To be able to manually order QA's.", verbose_name='Relative Order', blank=True)),
            ],
            options={
                'ordering': ('topic', 'order'),
                'verbose_name': 'QA',
            },
        ),
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100, verbose_name='Name')),
                ('fa_icon', models.CharField(max_length=50, verbose_name='FA Icon Name', blank=True)),
                ('slug', models.SlugField(max_length=100, verbose_name='Slug', blank=True)),
                ('order', models.IntegerField(default=0, help_text=b'To be able to manually order Topics.', verbose_name='Relative Order', blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='qa',
            name='topic',
            field=models.ForeignKey(related_name='qas', to='contact.Topic'),
        ),
    ]
