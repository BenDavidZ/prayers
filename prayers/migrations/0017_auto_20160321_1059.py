# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-03-21 15:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prayers', '0016_prayerfile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='prayerfile',
            name='file_name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
