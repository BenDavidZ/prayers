# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-30 19:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prayers', '0008_auto_20151228_2147'),
    ]

    operations = [
        migrations.AddField(
            model_name='prayer',
            name='curr_assigned_to',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='prayer',
            name='reassign',
            field=models.BooleanField(default=False),
        ),
    ]
