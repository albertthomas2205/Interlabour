from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import EmailOTP, PendingRegistration, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    list_display = ("id", "email", "username", "user_type", "email_verified", "is_staff", "is_active")
    list_filter = ("user_type", "email_verified", "is_staff", "is_active")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-id",)

    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Role and Verification", {"fields": ("user_type", "email_verified")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Role and Verification", {"fields": ("email", "user_type", "email_verified")}),
    )


@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "user", "purpose", "is_used", "attempts", "expires_at", "created_at")
    list_filter = ("purpose", "is_used")
    search_fields = ("email", "user__email")


@admin.register(PendingRegistration)
class PendingRegistrationAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "user_type", "is_used", "attempts", "expires_at", "created_at")
    list_filter = ("user_type", "is_used")
    search_fields = ("email", "first_name", "last_name")
