#!/usr/bin/env sh
set -eu

echo "Starting Render entrypoint..."
echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Optional: bootstrap application users from environment variables.
# This is idempotent: existing users are updated in place.
echo "Ensuring bootstrap users..."
python - <<'PY'
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def upsert_user(*, email, password, username="", is_superuser=False, is_staff=False, user_type="normal", email_verified=True):
    email = (email or "").strip()
    password = (password or "").strip()
    username = (username or "").strip()
    if not (email and password):
        return

    user = User.objects.filter(email=email).first()
    if user is None:
        create_kwargs = {
            "email": email,
            "password": password,
            "is_staff": is_staff,
            "is_superuser": is_superuser,
            "is_active": True,
            "user_type": user_type,
            "email_verified": email_verified,
        }
        if username:
            create_kwargs["username"] = username
        if is_superuser:
            User.objects.create_superuser(**create_kwargs)
        else:
            User.objects.create_user(**create_kwargs)
        return

    if username:
        user.username = username
    user.email = email
    user.is_active = True
    user.is_staff = is_staff
    user.is_superuser = is_superuser
    if hasattr(user, "user_type"):
        user.user_type = user_type
    if hasattr(user, "email_verified"):
        user.email_verified = email_verified
    user.set_password(password)
    user.save()


upsert_user(
    username=os.getenv("DJANGO_SUPERUSER_USERNAME", "admin"),
    email=os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@gmail.com"),
    password=os.getenv("DJANGO_SUPERUSER_PASSWORD", "admin123"),
    is_superuser=True,
    is_staff=True,
    user_type="admin",
    email_verified=True,
)

upsert_user(
    username=os.getenv("BOOTSTRAP_USER_USERNAME", "albert"),
    email=os.getenv("BOOTSTRAP_USER_EMAIL", "albert@gmail.com"),
    password=os.getenv("BOOTSTRAP_USER_PASSWORD", "albert123"),
    is_superuser=False,
    is_staff=False,
    user_type="normal",
    email_verified=True,
)
PY

PORT="${PORT:-10000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"
GUNICORN_THREADS="${GUNICORN_THREADS:-4}"
GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-120}"

echo "Starting Gunicorn on port ${PORT}..."
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY}" \
  --threads "${GUNICORN_THREADS}" \
  --timeout "${GUNICORN_TIMEOUT}"
