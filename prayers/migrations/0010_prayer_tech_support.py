# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-31 15:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prayers', '0009_auto_20151230_1931'),
    ]

    operations = [
        migrations.AddField(
            model_name='prayer',
            name='tech_support',
            field=models.BooleanField(default=False),
        ),
    ]
