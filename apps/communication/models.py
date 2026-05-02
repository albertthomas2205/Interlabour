from django.db import models


class ContactMessage(models.Model):
    class MessageStatus(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"

    name = models.CharField(max_length=160)
    email = models.EmailField()
    subject = models.CharField(max_length=220)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=MessageStatus.choices, default=MessageStatus.NEW)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name}: {self.subject}"
