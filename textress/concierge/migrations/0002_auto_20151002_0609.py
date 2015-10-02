# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('concierge', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reply',
            name='hotel',
            field=models.ForeignKey(blank=True, to='main.Hotel', null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='guest',
            field=models.ForeignKey(to='concierge.Guest'),
        ),
        migrations.AddField(
            model_name='message',
            name='hotel',
            field=models.ForeignKey(related_name='messages', blank=True, to='main.Hotel', null=True),
        ),
        migrations.AddField(
            model_name='message',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text=b'NULL unless sent from a Hotel User.', null=True),
        ),
        migrations.AddField(
            model_name='guest',
            name='hotel',
            field=models.ForeignKey(to='main.Hotel'),
        ),
        migrations.AddField(
            model_name='guest',
            name='icon',
            field=models.ForeignKey(blank=True, to='main.Icon', null=True),
        ),
    ]
