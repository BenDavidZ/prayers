# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-15 20:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prayers', '0013_auto_20160114_2208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prayer',
            name='response_text',
            field=models.TextField(blank=True, null=True),
        ),
    ]
