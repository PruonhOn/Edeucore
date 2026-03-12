from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Department

@admin.register(Department)
class DeptAdmin(admin.ModelAdmin):
    list_display = ['name','code']

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['username','first_name','last_name','role','department','is_active']
    list_filter = ['role','department']
    fieldsets = UserAdmin.fieldsets + (
        ('Extra', {'fields': ('role','department','phone','profile_picture','student_id','date_of_birth','gender','bio','address')}),
    )
