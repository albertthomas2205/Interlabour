from django.db import models


class CandidateProfile(models.Model):
    full_name = models.CharField(max_length=180)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=180, blank=True)
    title = models.CharField(max_length=180, blank=True)
    summary = models.TextField(blank=True)
    years_experience = models.PositiveSmallIntegerField(default=0)
    skills = models.TextField(blank=True, help_text="Comma-separated skills list.")
    portfolio_url = models.URLField(blank=True)
    avatar_url = models.URLField(blank=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]

    def __str__(self) -> str:
        return self.full_name
