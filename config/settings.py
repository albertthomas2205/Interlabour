import os
from datetime import timedelta
from pathlib import Path

try:
    import dj_database_url
except ImportError:
    dj_database_url = None

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        return False


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "change-me-in-production")
DEBUG = env_bool("DJANGO_DEBUG", True)
ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",") if h.strip()]

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "apps.accounts",
    "apps.jobs",
    "apps.applications",
    "apps.adminpanel",
    "apps.people",
    "apps.content",
    "apps.communication",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Our middleware fully owns language selection (?lang=, session, cookie),
    # so we intentionally do NOT use Django's LocaleMiddleware here.
    "config.i18n.QueryStringSessionLanguageMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            # Explicit registration so {% load il_admin_i18n %} always resolves (discovery can skip on some setups).
            "libraries": {
                "il_admin_i18n": "apps.adminpanel.templatetags.il_admin_i18n",
            },
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

database_url = os.getenv("DATABASE_URL")
if database_url and dj_database_url:
    DATABASES = {
        "default": dj_database_url.parse(database_url, conn_max_age=600, ssl_require=False),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "accounts.User"

LANGUAGE_CODE = "nl"
LANGUAGES = [
    ("nl", "Dutch"),
    ("en", "English"),
]
LOCALE_PATHS = [BASE_DIR / "locale"]
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"

STATIC_URL = "/assets/"
STATICFILES_DIRS = [
    BASE_DIR / "frontend" / "assets",
]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOW_ALL_ORIGINS = env_bool("CORS_ALLOW_ALL_ORIGINS", True)
cors_allowed = os.getenv("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_allowed.split(",") if origin.strip()]

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTES", "30"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=int(os.getenv("JWT_REFRESH_DAYS", "7"))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

OTP_EXPIRY_MINUTES = int(os.getenv("OTP_EXPIRY_MINUTES", "10"))
OTP_MAX_ATTEMPTS = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))

email_backend_from_env = os.getenv("EMAIL_BACKEND")
if email_backend_from_env:
    EMAIL_BACKEND = email_backend_from_env
elif os.getenv("EMAIL_HOST_USER") and os.getenv("EMAIL_HOST_PASSWORD"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = env_bool("EMAIL_USE_SSL", False)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "no-reply@interlabour.local")

# Separate Zoho mailboxes (optional). If set, we can send different emails from different mailboxes.
SUPPORT_EMAIL_HOST_USER = os.getenv("SUPPORT_EMAIL_HOST_USER", "").strip()
SUPPORT_EMAIL_HOST_PASSWORD = os.getenv("SUPPORT_EMAIL_HOST_PASSWORD", "").strip()
SUPPORT_FROM_EMAIL = os.getenv("SUPPORT_FROM_EMAIL", "").strip() or SUPPORT_EMAIL_HOST_USER or DEFAULT_FROM_EMAIL

HR_EMAIL_HOST_USER = os.getenv("HR_EMAIL_HOST_USER", "").strip()
HR_EMAIL_HOST_PASSWORD = os.getenv("HR_EMAIL_HOST_PASSWORD", "").strip()
HR_FROM_EMAIL = os.getenv("HR_FROM_EMAIL", "").strip() or HR_EMAIL_HOST_USER or DEFAULT_FROM_EMAIL

# Sender for OTP verification e-mails (should match SMTP allowlist when using Zoho etc.).
_OTP_FE = os.getenv("OTP_FROM_EMAIL", "").strip()
OTP_FROM_EMAIL = _OTP_FE or DEFAULT_FROM_EMAIL
# Mailbox only (optional). If set, overrides the address in OTP_FROM_EMAIL for the From header.
_OTP_MB = os.getenv("OTP_FROM_MAILBOX", "").strip()
OTP_FROM_MAILBOX = _OTP_MB

# Public site URL used to build absolute image URLs in HTML emails (fallback logo).
# Example: https://www.interlabour.nl — no trailing slash. Prefer inline PNG or EMAIL_LOGO_URL.
PUBLIC_SITE_URL = os.getenv("PUBLIC_SITE_URL", "").strip().rstrip("/")
# Optional absolute URL for the logo in emails (CDN or static host). When set, inline attachment is skipped.
EMAIL_LOGO_URL = os.getenv("EMAIL_LOGO_URL", "").strip()
# Embed frontend/assets/imgs/theme/logo-email.png as CID attachment (recommended; works in Gmail/Outlook).
EMAIL_INLINE_LOGO = env_bool("EMAIL_INLINE_LOGO", True)

SPECTACULAR_SETTINGS = {
    "TITLE": "Inter Labour API",
    "DESCRIPTION": "Backend API for the Inter Labour job board frontend.",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
