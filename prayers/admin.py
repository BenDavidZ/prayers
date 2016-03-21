from django.contrib import admin
from trix.admin import TrixAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from prayers.models import Prayer, Employee, PrayerFile

# Register your models here.


class EmployeeInline(admin.StackedInline):
    model = Employee
    can_delete = False
    verbose_name_plural = 'employee'


class UserAdmin(BaseUserAdmin):
    inlines = (EmployeeInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active')


class PrayerAdmin(TrixAdmin, admin.ModelAdmin):
    trix_fields = ('response_text')
    list_display = ('user_name', 'user_email', 'originating_ministry', 'assigned_to', 'response_by')
    list_filter = ['assigned_to', 'originating_ministry', 'created_at']
    search_fields = ['user_name', 'user_email', 'user_request', 'created_at']

admin.site.register(Prayer, PrayerAdmin)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(PrayerFile)
