import logging
from email.mime.image import MIMEImage
from pathlib import Path

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils import translation

from .models import Application

logger = logging.getLogger(__name__)

APP_UPDATE_LOGO_CID = "il_app_update_logo"

STATUS_NL = {
    Application.ApplicationStatus.SUBMITTED: "Ingediend",
    Application.ApplicationStatus.REVIEWING: "In behandeling",
    Application.ApplicationStatus.REJECTED: "Afgewezen",
    Application.ApplicationStatus.HIRED: "Aangenomen",
}

STATUS_EN = {
    Application.ApplicationStatus.SUBMITTED: "Submitted",
    Application.ApplicationStatus.REVIEWING: "Reviewing",
    Application.ApplicationStatus.REJECTED: "Rejected",
    Application.ApplicationStatus.HIRED: "Hired",
}


def _logo_path() -> Path:
    return settings.BASE_DIR / "frontend" / "assets" / "imgs" / "theme" / "logo-email.png"


def _attach_inline_logo_png(message: EmailMultiAlternatives, path: Path) -> None:
    with path.open("rb") as f:
        img = MIMEImage(f.read(), _subtype="png")
    img.add_header("Content-ID", f"<{APP_UPDATE_LOGO_CID}>")
    img.add_header("Content-Disposition", "inline", filename="logo-email.png")
    message.attach(img)


def send_application_status_update_email(
    application: Application,
    *,
    old_status: str | None,
    new_status: str,
) -> None:
    """
    Notify the applicant when an admin updates an application status.

    We render Dutch first and include an English section underneath so users do
    not need Gmail/Zoho translation (which can break email HTML).
    """
    recipient = (getattr(application, "email", "") or "").strip()
    if not recipient:
        return

    job = getattr(application, "job", None)
    company_name = getattr(getattr(job, "company", None), "name", "") if job else ""
    job_title = getattr(job, "title_i18n", "") or getattr(job, "title", "") if job else ""

    old_nl = STATUS_NL.get(old_status, "-") if old_status else "-"
    new_nl = STATUS_NL.get(new_status, new_status)
    old_en = STATUS_EN.get(old_status, "-") if old_status else "-"
    new_en = STATUS_EN.get(new_status, new_status)

    context = {
        "recipient_name": (application.full_name or "").strip() or "daar",
        "application_id": application.pk,
        "job_title": job_title,
        "company_name": company_name,
        "old_status_nl": old_nl,
        "new_status_nl": new_nl,
        "old_status_en": old_en,
        "new_status_en": new_en,
        "updated_at": timezone.localtime(getattr(application, "updated_at", None) or timezone.now()),
        "site_url": getattr(settings, "PUBLIC_SITE_URL", "").strip().rstrip("/"),
        "logo_cid": APP_UPDATE_LOGO_CID,
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

    if getattr(settings, "EMAIL_INLINE_LOGO", True):
        logo = _logo_path()
        if logo.is_file():
            try:
                _attach_inline_logo_png(msg, logo)
            except OSError:
                logger.exception("Could not attach inline logo for application update email")

    msg.send(fail_silently=False)


def send_application_submitted_email(application: Application) -> None:
    """Confirmation email when a user submits a job application (from HR mailbox)."""
    recipient = (getattr(application, "email", "") or "").strip()
    if not recipient:
        return

    job = getattr(application, "job", None)
    company_name = getattr(getattr(job, "company", None), "name", "") if job else ""
    job_title = getattr(job, "title_i18n", "") or getattr(job, "title", "") if job else ""

    context = {
        "recipient_name": (application.full_name or "").strip() or "daar",
        "application_id": application.pk,
        "job_title": job_title,
        "company_name": company_name,
        "submitted_at": timezone.localtime(getattr(application, "applied_at", None) or timezone.now()),
        "site_url": getattr(settings, "PUBLIC_SITE_URL", "").strip().rstrip("/"),
        "logo_cid": APP_UPDATE_LOGO_CID,
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

    if getattr(settings, "EMAIL_INLINE_LOGO", True):
        logo = _logo_path()
        if logo.is_file():
            try:
                _attach_inline_logo_png(msg, logo)
            except OSError:
                logger.exception("Could not attach inline logo for application submitted email")

    msg.send(fail_silently=False)

