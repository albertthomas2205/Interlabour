import logging
from email.utils import formataddr, parseaddr

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import translation

from config.email_branding import attach_interlabour_logo_png, interlabour_branding_for_message

from .models import EmailOTP, PendingRegistration

logger = logging.getLogger(__name__)


def _otp_from_email_header() -> str:
    """
    Build the visible From header for OTP mail. We always send through the
    SUPPORT_EMAIL_HOST_USER mailbox (separate Zoho mailbox) and the From header
    is derived from OTP_FROM_EMAIL / OTP_FROM_MAILBOX. The auth user used for
    the SMTP connection must match the visible From — that's enforced below.
    """
    raw = (getattr(settings, "OTP_FROM_EMAIL", None) or "").strip()
    if not raw:
        raw = (getattr(settings, "SUPPORT_FROM_EMAIL", None) or "").strip() or (getattr(settings, "DEFAULT_FROM_EMAIL", None) or "").strip()
    display_name, parsed_mailbox = parseaddr(raw)

    mailbox_override = (getattr(settings, "OTP_FROM_MAILBOX", None) or "").strip()
    mailbox = mailbox_override or parsed_mailbox
    if not mailbox or "@" not in mailbox:
        fallback = (getattr(settings, "SUPPORT_EMAIL_HOST_USER", None) or "").strip() or (getattr(settings, "EMAIL_HOST_USER", None) or "").strip()
        if not fallback:
            fallback = "support@interlabour.nl"
        mailbox = fallback

    # Compare against SUPPORT_EMAIL_HOST_USER (the actual SMTP auth user used
    # by the OTP flow) instead of EMAIL_HOST_USER — the previous comparison
    # produced a misleading warning whenever HR and support mailboxes differed.
    support_user = (getattr(settings, "SUPPORT_EMAIL_HOST_USER", None) or "").strip()
    if support_user and mailbox.lower() != support_user.lower():
        logger.warning(
            "OTP From-header is %r but SMTP authenticates as %r — Zoho may "
            "reject the message or rewrite the sender. They should match.",
            mailbox,
            support_user,
        )

    if display_name:
        return formataddr((display_name, mailbox))
    return mailbox


def _otp_subject() -> str:
    return "Inter Labour — jouw verificatiecode"


def _otp_email_context(
    recipient_first_line: str,
    otp_code: str,
    *,
    language_code: str,
    logo_cid: str | None,
    logo_url: str,
    purpose: str = "registration",
) -> dict:
    expiry = int(getattr(settings, "OTP_EXPIRY_MINUTES", 10))
    site = getattr(settings, "PUBLIC_SITE_URL", "").strip().rstrip("/")
    return {
        "recipient_name": recipient_first_line,
        "otp_code": otp_code,
        "expiry_minutes": expiry,
        "logo_cid": logo_cid,
        "logo_url": logo_url,
        "site_url": site,
        "email_locale": language_code,
        "purpose": purpose,
    }


def _send_otp_email(
    recipient_email: str,
    recipient_first_line: str,
    otp_code: str,
    *,
    language_code: str | None = None,
    purpose: str = "registration",
) -> None:
    branding, attach_png = interlabour_branding_for_message()

    support_user = (getattr(settings, "SUPPORT_EMAIL_HOST_USER", "") or "").strip()
    support_pass = (getattr(settings, "SUPPORT_EMAIL_HOST_PASSWORD", "") or "").strip()
    connection = (
        get_connection(username=support_user, password=support_pass)
        if support_user and support_pass
        else None
    )

    # Transactional e-mails are Dutch-only regardless of UI language.
    with translation.override("nl"):
        context = _otp_email_context(
            recipient_first_line,
            otp_code,
            language_code="nl",
            logo_cid=branding.get("logo_cid"),
            logo_url=branding.get("logo_url") or "",
            purpose=purpose,
        )
        subject = _otp_subject()
        text_body = render_to_string("emails/otp_verification.txt", context)
        html_body = render_to_string("emails/otp_verification.html", context)

    from_email = _otp_from_email_header()
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=[recipient_email],
        connection=connection,
    )
    msg.attach_alternative(html_body, "text/html")

    attach_interlabour_logo_png(msg, attach_png)

    # In DEBUG mode, always echo the code to the runserver console so a developer
    # can finish the flow even if the email is delayed or filtered as spam.
    if getattr(settings, "DEBUG", False):
        try:
            print(
                "\n" + "=" * 60 +
                f"\n[OTP] purpose={purpose} to={recipient_email}\n[OTP] CODE = {otp_code}\n" +
                "=" * 60 + "\n",
                flush=True,
            )
        except Exception:
            pass

    try:
        sent = msg.send(fail_silently=False)
    except Exception as exc:
        logger.exception(
            "OTP email send failed (purpose=%s, to=%s, from=%s, smtp_user=%s, host=%s:%s): %s",
            purpose,
            recipient_email,
            from_email,
            support_user or getattr(settings, "EMAIL_HOST_USER", ""),
            getattr(settings, "EMAIL_HOST", ""),
            getattr(settings, "EMAIL_PORT", ""),
            exc,
        )
        raise

    if not sent:
        logger.error(
            "OTP email reported 0 messages sent (purpose=%s, to=%s)",
            purpose,
            recipient_email,
        )
        raise RuntimeError("Email server accepted the request but did not send the message.")

    logger.info(
        "OTP email sent (purpose=%s, to=%s, from=%s)",
        purpose,
        recipient_email,
        from_email,
    )


def send_registration_otp(user, *, language_code: str | None = None):
    otp_record, otp_code = EmailOTP.create_for_user(user=user, purpose=EmailOTP.Purpose.REGISTRATION)

    display = (user.first_name or "").strip() or (user.email.split("@")[0] if user.email else "there")
    _send_otp_email(
        user.email,
        display,
        otp_code,
        language_code=language_code,
        purpose="registration",
    )

    return otp_record


def send_pending_registration_otp(
    pending: PendingRegistration,
    otp_code: str,
    *,
    language_code: str | None = None,
):
    display = (pending.first_name or "").strip() or pending.email.split("@")[0]
    _send_otp_email(
        pending.email,
        display,
        otp_code,
        language_code=language_code,
        purpose="registration",
    )


def send_password_reset_otp(user, *, language_code: str | None = None):
    """Generate a fresh PASSWORD_RESET OTP for the user and email it."""
    EmailOTP.objects.filter(
        user=user,
        purpose=EmailOTP.Purpose.PASSWORD_RESET,
        is_used=False,
    ).update(is_used=True)

    otp_record, otp_code = EmailOTP.create_for_user(
        user=user, purpose=EmailOTP.Purpose.PASSWORD_RESET
    )

    display = (user.first_name or "").strip() or (
        user.email.split("@")[0] if user.email else "there"
    )
    _send_otp_email(
        user.email,
        display,
        otp_code,
        language_code=language_code,
        purpose="password_reset",
    )

    return otp_record
