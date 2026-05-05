import logging
from email.mime.image import MIMEImage
from email.utils import formataddr, parseaddr
from pathlib import Path

from django.conf import settings
from django.core.mail import get_connection
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import gettext as _

from config.i18n import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

from .models import EmailOTP, PendingRegistration

logger = logging.getLogger(__name__)

OTP_EMAIL_LOGO_CID = "il_otp_logo"


def _normalize_email_language(language_code: str | None) -> str:
    if not language_code:
        code = DEFAULT_LANGUAGE if DEFAULT_LANGUAGE in SUPPORTED_LANGUAGES else "nl"
        return code
    c = language_code.strip().lower()
    return c if c in SUPPORTED_LANGUAGES else (DEFAULT_LANGUAGE if DEFAULT_LANGUAGE in SUPPORTED_LANGUAGES else "nl")


def _otp_inline_logo_png_path() -> Path:
    return settings.BASE_DIR / "frontend" / "assets" / "imgs" / "theme" / "logo-email.png"


def _otp_logo_remote_url() -> str:
    if getattr(settings, "EMAIL_LOGO_URL", ""):
        return settings.EMAIL_LOGO_URL.strip()
    base = getattr(settings, "PUBLIC_SITE_URL", "").strip().rstrip("/")
    if not base:
        return ""
    prefix = getattr(settings, "STATIC_URL", "/assets/").strip("/")
    return f"{base}/{prefix}/imgs/theme/logo-email.png"


def _otp_branding_for_message() -> tuple[dict, Path | None]:
    """Logo for template plus optional PNG path for inline CID attachment."""
    explicit = (getattr(settings, "EMAIL_LOGO_URL", None) or "").strip()
    if explicit:
        return {"logo_cid": None, "logo_url": explicit}, None

    use_inline = getattr(settings, "EMAIL_INLINE_LOGO", True)
    png = _otp_inline_logo_png_path()
    if use_inline and png.is_file():
        return {"logo_cid": OTP_EMAIL_LOGO_CID, "logo_url": ""}, png

    return {"logo_cid": None, "logo_url": _otp_logo_remote_url()}, None


def _attach_inline_logo_png(message: EmailMultiAlternatives, path: Path) -> None:
    with path.open("rb") as f:
        img = MIMEImage(f.read(), _subtype="png")
    img.add_header("Content-ID", f"<{OTP_EMAIL_LOGO_CID}>")
    img.add_header("Content-Disposition", "inline", filename="logo-email.png")
    message.attach(img)


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
    return _("Inter Labour - your verification code")


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
    lang = _normalize_email_language(language_code)
    branding, attach_png = _otp_branding_for_message()

    support_user = (getattr(settings, "SUPPORT_EMAIL_HOST_USER", "") or "").strip()
    support_pass = (getattr(settings, "SUPPORT_EMAIL_HOST_PASSWORD", "") or "").strip()
    connection = (
        get_connection(username=support_user, password=support_pass)
        if support_user and support_pass
        else None
    )

    with translation.override(lang):
        context = _otp_email_context(
            recipient_first_line,
            otp_code,
            language_code=lang,
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

    if attach_png:
        try:
            _attach_inline_logo_png(msg, attach_png)
        except OSError:
            logger.exception("Could not attach inline OTP logo from %s", attach_png)

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
