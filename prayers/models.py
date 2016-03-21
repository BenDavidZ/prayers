from django.db import models
from django.dispatch import receiver
from django.forms import ModelForm
from django.utils import timezone
from django.core.urlresolvers import reverse
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django import forms
from trix.widgets import TrixEditor

import datetime


class UploadFileForm(forms.Form):
    prayer_file = forms.FileField()


class Prayer(models.Model):
    created_at = models.DateTimeField('date received', auto_now_add=True)
    updated_at = models.DateTimeField('date updated', auto_now=True)
    user_name = models.CharField(max_length=100)
    user_email = models.EmailField()
    user_request = models.TextField()
    received_at = models.DateTimeField(null=True, blank=True)
    email_subject = models.CharField(max_length=100, null=True, blank=True)
    assigned_to = models.ForeignKey(User, limit_choices_to={'is_superuser': False, 'is_active': True}, null=True, blank=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    prayed_by = models.CharField(max_length=50, null=True, blank=True)
    prayed_at = models.DateTimeField(null=True, blank=True)
    response_text = models.TextField(null=True, blank=True)
    response_by = models.CharField(max_length=50, null=True, blank=True)
    response_at = models.DateTimeField(null=True, blank=True)
    originating_ministry = models.CharField(max_length=50, null=True)
    response_in_progress = models.BooleanField(default=False)  # may not need
    in_prayer = models.BooleanField(default=False)  # consider removing
    is_new = models.BooleanField(default=True)  # may not need either
    staff_request = models.CharField(max_length=50, null=True, blank=True)
    reassign = models.BooleanField(default=False)
    tech_support = models.BooleanField(default=False)
    curr_assigned_to = models.CharField(max_length=50, null=True, blank=True)

    def __unicode__(self):
        return self.user_name

    def get_absolute_url(self):
        return reverse('prayers:index')


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.CharField(max_length=50, null=True, blank=True)
    unprayed_count = models.IntegerField(default=0)

    def __unicode__(self):
        return self.user.username


class DeleteForm(ModelForm):
    class Meta:
        model = Prayer
        fields = ['user_name', 'user_email', 'user_request']


class PrayerForm(ModelForm):
    class Meta:
        model = Prayer
        fields = ['user_name', 'user_email', 'originating_ministry', 'user_request', 'received_at']


class StaffAssignForm(ModelForm):
    class Meta:
        model = Prayer
        fields = ['user_name', 'user_email', 'user_request', 'staff_request', 'assigned_to']


class PrayerResponseForm(ModelForm):
    response_text = forms.CharField(widget=TrixEditor)

    class Meta:
        model = Prayer
        fields = ['response_text']


@receiver(post_save, sender=User)
def ensure_profile_exists(sender, **kwargs):
    if kwargs.get('created', False):
        Employee.objects.get_or_create(user=kwargs.get('instance'))
