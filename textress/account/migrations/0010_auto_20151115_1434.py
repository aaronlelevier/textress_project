# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20151029_0635'),
        ('account', '0009_auto_20151115_1225'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pricing',
            options={'verbose_name_plural': 'Pricing'},
        ),
        migrations.RemoveField(
            model_name='pricing',
            name='desc',
        ),
        migrations.RemoveField(
            model_name='pricing',
            name='end',
        ),
        migrations.RemoveField(
            model_name='pricing',
            name='price',
        ),
        migrations.RemoveField(
            model_name='pricing',
            name='start',
        ),
        migrations.RemoveField(
            model_name='pricing',
            name='tier',
        ),
        migrations.RemoveField(
            model_name='pricing',
            name='tier_name',
        ),
        migrations.AddField(
            model_name='pricing',
            name='cost',
            field=models.FloatField(default=5.0, help_text=b'Price in Stripe units, so -> 5.00 == $0.05', blank=True),
        ),
        migrations.AddField(
            model_name='pricing',
            name='hotel',
            field=models.OneToOneField(related_name='pricing', null=True, blank=True, to='main.Hotel'),
        ),
    ]
