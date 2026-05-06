from django.db.models.signals import post_save
from django.dispatch import receiver

from .emailing import send_new_job_alerts
from .models import Job


@receiver(post_save, sender=Job)
def _job_created_send_alerts(sender, instance: Job, created: bool, **kwargs):
    # Only notify on first create; avoids sending on edits.
    if created and getattr(instance, "is_active", False):
        try:
            send_new_job_alerts(instance)
        except Exception:
            # Never block job creation on email failures.
            pass

