import logging
from urllib.parse import urlencode

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from config.email_branding import attach_interlabour_logo_png, interlabour_branding_for_message

from .models import Job, JobAlertSubscription

logger = logging.getLogger(__name__)


def send_job_alert_subscription_confirmation_email(email: str, *, language_code: str = "nl") -> None:
    """Bevestiging in het Nederlands wanneer iemand zich inschrijft voor vacaturemeldingen.

    `language_code` wordt genegeerd: transactionele e-mail is altijd Nederlands.
    """
    recipient = (email or "").strip().lower()
    if not recipient or "@" not in recipient:
        return

    site = getattr(settings, "PUBLIC_SITE_URL", "").strip().rstrip("/")
    jobs_url = f"{site}/jobs/" if site else "/jobs/"
    confirm_path = "/jobs/alerts/confirmed/"
    confirm_url = (
        f"{site}{confirm_path}?{urlencode({'email': recipient, 'lang': 'nl'})}"
        if site
        else f"{confirm_path}?{urlencode({'email': recipient, 'lang': 'nl'})}"
    )

    branding, logo_path = interlabour_branding_for_message()

    context = {
        "email": recipient,
        "site_url": site,
        "jobs_url": jobs_url,
        "confirm_url": confirm_url,
        "email_locale": "nl",
        **branding,
    }

    subject = "Bevestiging vacaturemeldingen — Inter Labour"
    from_email = getattr(settings, "HR_FROM_EMAIL", "") or getattr(settings, "DEFAULT_FROM_EMAIL", "")

    hr_user = (getattr(settings, "HR_EMAIL_HOST_USER", "") or "").strip()
    hr_pass = (getattr(settings, "HR_EMAIL_HOST_PASSWORD", "") or "").strip()
    connection = get_connection(username=hr_user, password=hr_pass) if hr_user and hr_pass else None

    text_body = render_to_string("emails/job_alert_subscription_confirmed.txt", context)
    html_body = render_to_string("emails/job_alert_subscription_confirmed.html", context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=[recipient],
        connection=connection,
    )
    msg.attach_alternative(html_body, "text/html")
    attach_interlabour_logo_png(msg, logo_path)
    try:
        msg.send(fail_silently=False)
    except Exception:
        logger.exception("Failed sending job-alert subscription confirmation to %s", recipient)
        raise


def send_new_job_alerts(job: Job) -> int:
    """Send a bilingual (NL + EN) email notification for a newly published job."""
    if not job or not getattr(job, "slug", ""):
        return 0
    if not getattr(job, "is_active", False):
        return 0

    recipients = list(
        JobAlertSubscription.objects.filter(is_active=True)
        .exclude(email="")
        .values_list("email", flat=True)
    )
    if not recipients:
        return 0

    site = getattr(settings, "PUBLIC_SITE_URL", "").strip().rstrip("/")
    job_url = f"{site}/jobs/{job.slug}/" if site else f"/jobs/{job.slug}/"

    branding, logo_path = interlabour_branding_for_message()

    context = {
        "job": job,
        "job_url": job_url,
        "site_url": site,
        "title_nl": (job.title_nl or job.title_en or job.title or "").strip(),
        "title_en": (job.title_en or job.title_nl or job.title or "").strip(),
        "location": (job.location or "").strip(),
        "company_name": (getattr(getattr(job, "company", None), "name", "") or "").strip(),
        "excerpt_nl": (job.description_nl or job.description_en or job.description or "").strip(),
        "excerpt_en": (job.description_en or job.description_nl or job.description or "").strip(),
        **branding,
    }

    subject = f"Nieuwe vacature: {context['title_nl'] or context['title_en']}".strip()
    from_email = getattr(settings, "HR_FROM_EMAIL", "") or getattr(settings, "DEFAULT_FROM_EMAIL", "")

    hr_user = (getattr(settings, "HR_EMAIL_HOST_USER", "") or "").strip()
    hr_pass = (getattr(settings, "HR_EMAIL_HOST_PASSWORD", "") or "").strip()
    connection = get_connection(username=hr_user, password=hr_pass) if hr_user and hr_pass else None

    text_body = render_to_string("emails/job_alert_new_job.txt", context)
    html_body = render_to_string("emails/job_alert_new_job.html", context)

    sent = 0
    for recipient in recipients:
        try:
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_body,
                from_email=from_email,
                to=[recipient],
                connection=connection,
            )
            msg.attach_alternative(html_body, "text/html")
            attach_interlabour_logo_png(msg, logo_path)
            msg.send(fail_silently=False)
            sent += 1
        except Exception:
            logger.exception("Failed sending job alert to %s (job=%s)", recipient, getattr(job, "pk", None))
    return sent

