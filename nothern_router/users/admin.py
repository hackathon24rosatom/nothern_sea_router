from django.conf import settings
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from .models import User, Staff, Company


admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    add_fieldsets = (
        ('Identification', {
            'classes': ('wide',),
            'fields': ('email', 'username')}
         ),
        ('Advanced Options', {
            'fields': ('first_name', 'last_name')}
         ),
    )
    search_fields = ('username',)
    ordering = ('username',)



@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    search_fields = ('name',)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
    search_fields = ('user', 'company')
