from django.conf import settings
from django.core.mail import get_connection
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils import translation

from config.email_branding import attach_interlabour_logo_png, interlabour_branding_for_message

from .models import Application

STATUS_NL = {
    Application.ApplicationStatus.SUBMITTED: "Ingediend",
    Application.ApplicationStatus.REVIEWING: "In behandeling",
    Application.ApplicationStatus.REJECTED: "Afgewezen",
    Application.ApplicationStatus.HIRED: "Aangenomen",
}


def send_application_status_update_email(
    application: Application,
    *,
    old_status: str | None,
    new_status: str,
) -> None:
    """Notify the applicant when an admin updates an application status (Dutch only)."""
    recipient = (getattr(application, "email", "") or "").strip()
    if not recipient:
        return

    job = getattr(application, "job", None)
    company_name = getattr(getattr(job, "company", None), "name", "") if job else ""
    job_title = getattr(job, "title_i18n", "") or getattr(job, "title", "") if job else ""

    new_nl = STATUS_NL.get(new_status, new_status)

    branding, logo_path = interlabour_branding_for_message()

    context = {
        "recipient_name": (application.full_name or "").strip() or "daar",
        "application_id": application.pk,
        "job_title": job_title,
        "company_name": company_name,
        "new_status_nl": new_nl,
        "updated_at": timezone.localtime(getattr(application, "updated_at", None) or timezone.now()),
        "site_url": getattr(settings, "PUBLIC_SITE_URL", "").strip().rstrip("/"),
        **branding,
    }

    subject = f"Update sollicitatie #{application.pk} - {new_nl}"
    from_email = getattr(settings, "HR_FROM_EMAIL", "") or getattr(settings, "DEFAULT_FROM_EMAIL", "")

    hr_user = (getattr(settings, "HR_EMAIL_HOST_USER", "") or "").strip()
    hr_pass = (getattr(settings, "HR_EMAIL_HOST_PASSWORD", "") or "").strip()
    connection = get_connection(username=hr_user, password=hr_pass) if hr_user and hr_pass else None

    with translation.override("nl"):
        text_body = render_to_string("emails/application_status_updated.txt", context)
        html_body = render_to_string("emails/application_status_updated.html", context)

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


def send_application_submitted_email(application: Application) -> None:
    """Confirmation email when a user submits a job application (from HR mailbox)."""
    recipient = (getattr(application, "email", "") or "").strip()
    if not recipient:
        return

    job = getattr(application, "job", None)
    company_name = getattr(getattr(job, "company", None), "name", "") if job else ""
    job_title = getattr(job, "title_i18n", "") or getattr(job, "title", "") if job else ""

    branding, logo_path = interlabour_branding_for_message()

    context = {
        "recipient_name": (application.full_name or "").strip() or "daar",
        "application_id": application.pk,
        "job_title": job_title,
        "company_name": company_name,
        "submitted_at": timezone.localtime(getattr(application, "applied_at", None) or timezone.now()),
        "site_url": getattr(settings, "PUBLIC_SITE_URL", "").strip().rstrip("/"),
        **branding,
    }

    subject = f"Sollicitatie ontvangen - #{application.pk}"
    from_email = getattr(settings, "HR_FROM_EMAIL", "") or getattr(settings, "DEFAULT_FROM_EMAIL", "")

    hr_user = (getattr(settings, "HR_EMAIL_HOST_USER", "") or "").strip()
    hr_pass = (getattr(settings, "HR_EMAIL_HOST_PASSWORD", "") or "").strip()
    connection = get_connection(username=hr_user, password=hr_pass) if hr_user and hr_pass else None

    with translation.override("nl"):
        text_body = render_to_string("emails/application_submitted.txt", context)
        html_body = render_to_string("emails/application_submitted.html", context)

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
