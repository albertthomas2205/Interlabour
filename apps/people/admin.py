from django.contrib import admin

from .models import CandidateProfile


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "email", "location", "is_available", "created_at")
    list_filter = ("is_available",)
    search_fields = ("full_name", "email", "location")
