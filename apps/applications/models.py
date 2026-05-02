from django.conf import settings
from django.db import models


class Application(models.Model):
    class ApplicationStatus(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        REVIEWING = "reviewing", "Reviewing"
        REJECTED = "rejected", "Rejected"
        HIRED = "hired", "Hired"

    job = models.ForeignKey("jobs.Job", on_delete=models.CASCADE, related_name="applications")
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="job_applications",
        null=True,
        blank=True,
    )
    full_name = models.CharField(max_length=180)
    email = models.EmailField()
    phone = models.CharField(max_length=50, blank=True)
    # Required for new submissions, but allow NULL in DB for existing rows.
    resume = models.FileField(upload_to="applications/resumes/", null=True, blank=False)
    aadhaar_card = models.FileField(
        upload_to="applications/aadhaar/",
        null=True,
        blank=True,
        help_text="Aadhaar Card (mandatory)",
    )
    pan_card = models.FileField(
        upload_to="applications/pan/",
        null=True,
        blank=True,
        help_text="PAN Card (mandatory)",
    )
    passport = models.FileField(
        upload_to="applications/passport/",
        null=True,
        blank=True,
        help_text="Passport (mandatory)",
    )
    cover_letter = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=ApplicationStatus.choices, default=ApplicationStatus.SUBMITTED
    )
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-applied_at"]
        constraints = [
            models.UniqueConstraint(fields=["job", "applicant"], name="unique_job_application_per_user"),
        ]
        db_table = "jobs_application"

    def __str__(self) -> str:
        job_title = getattr(self.job, "title", "")
        return f"{self.full_name} -> {job_title}"

