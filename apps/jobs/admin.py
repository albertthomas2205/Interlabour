from django.contrib import admin

from .models import Application, Company, Job, JobCategory


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "owner", "location", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "location", "owner__email")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "company", "job_type", "location", "is_active", "posted_at")
    list_filter = ("job_type", "experience_level", "is_featured", "is_active")
    search_fields = ("title", "location", "company__name")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "job", "applicant", "status", "applied_at")
    list_filter = ("status",)
    search_fields = ("full_name", "email", "job__title", "applicant__email")
