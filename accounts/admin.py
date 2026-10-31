from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, CustomerProfile


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'username', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Profile Fields', {'fields': ('role', 'phone_number')}),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'city', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'city')
