# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-07 20:38
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Prayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name=b'date received')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name=b'date updated')),
                ('user_name', models.CharField(max_length=20)),
                ('user_email', models.EmailField(max_length=254)),
                ('user_request', models.TextField()),
                ('assigned_at', models.DateTimeField(blank=True, null=True)),
                ('prayed_by', models.CharField(max_length=50, null=True)),
                ('prayed_at', models.DateTimeField(blank=True, null=True)),
                ('response_by', models.CharField(max_length=50, null=True)),
                ('response_at', models.DateTimeField(blank=True, null=True)),
                ('response_in_progress', models.BooleanField(default=False)),
                ('in_prayer', models.BooleanField(default=False)),
                ('is_new', models.BooleanField(default=True)),
                ('staff_request', models.CharField(blank=True, max_length=50, null=True)),
                ('assigned_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
