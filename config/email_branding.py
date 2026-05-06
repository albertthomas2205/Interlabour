"""Shared Inter Labour transactional email branding (logo CID / URL)."""

import logging
from email.mime.image import MIMEImage
from pathlib import Path

from django.conf import settings

logger = logging.getLogger(__name__)

# Single CID across all HTML templates so inline attachments stay consistent.
INTERLABOUR_LOGO_CID = "interlabour_logo"


def interlabour_logo_png_path() -> Path:
    return settings.BASE_DIR / "frontend" / "assets" / "imgs" / "theme" / "logo-email.png"


def interlabour_logo_remote_url() -> str:
    if getattr(settings, "EMAIL_LOGO_URL", ""):
        return settings.EMAIL_LOGO_URL.strip()
    base = getattr(settings, "PUBLIC_SITE_URL", "").strip().rstrip("/")
    if not base:
        return ""
    prefix = getattr(settings, "STATIC_URL", "/assets/").strip("/")
    return f"{base}/{prefix}/imgs/theme/logo-email.png"


def interlabour_branding_for_message() -> tuple[dict[str, str | None], Path | None]:
    """
    Returns (template_context_dict, optional_png_path_to_attach).
    Template expects keys: logo_cid, logo_url.
    """
    explicit = (getattr(settings, "EMAIL_LOGO_URL", None) or "").strip()
    if explicit:
        return {"logo_cid": None, "logo_url": explicit}, None

    use_inline = getattr(settings, "EMAIL_INLINE_LOGO", True)
    png = interlabour_logo_png_path()
    if use_inline and png.is_file():
        return {"logo_cid": INTERLABOUR_LOGO_CID, "logo_url": ""}, png

    return {"logo_cid": None, "logo_url": interlabour_logo_remote_url()}, None


def attach_interlabour_logo_png(message, path: Path | None) -> None:
    if path is None or not path.is_file():
        return
    try:
        with path.open("rb") as f:
            img = MIMEImage(f.read(), _subtype="png")
        img.add_header("Content-ID", f"<{INTERLABOUR_LOGO_CID}>")
        img.add_header("Content-Disposition", "inline", filename="logo-email.png")
        message.attach(img)
    except OSError:
        logger.exception("Could not attach Inter Labour inline logo from %s", path)
