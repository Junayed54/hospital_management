from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User  # Import the concrete CustomUser model

class UserAdmin(BaseUserAdmin):
    # List of fields to be displayed in the admin interface
    list_display = ('phone_number', 'role', 'is_active', 'is_verified', 'date_joined', 'is_superuser')
    list_filter = ('role', 'is_active', 'is_verified')  
    
    # Fields to display in the user details page
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),  # Password is already managed by Django auth
        ('Personal Info', {'fields': ('date_of_birth', 'gender', 'address', 'profile_picture')}),
        ('Emergency Contact', {'fields': ('emergency_contact_name', 'emergency_contact_phone')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),  # Readonly fields
    )

    # Fields to be displayed when adding a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2', 'role', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )

    # Fields for search and ordering in the admin panel
    search_fields = ('phone_number',)
    ordering = ('phone_number',)

    filter_horizontal = ('groups', 'user_permissions')  # Add these fields as horizontal filter choices
    readonly_fields = ('date_joined', 'last_login')  # Make 'date_joined' and 'last_login' read-only

# Register the custom User model with the admin site
admin.site.register(User, UserAdmin)
