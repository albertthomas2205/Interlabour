#!/usr/bin/env sh
set -eu

echo "Starting Render entrypoint..."
echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

# Optional: create a superuser non-interactively (only if env vars are set).
# Set these in Render Environment:
# - DJANGO_SUPERUSER_EMAIL
# - DJANGO_SUPERUSER_PASSWORD
# - DJANGO_SUPERUSER_USERNAME (optional)
echo "Ensuring optional superuser..."
python - <<'PY'
import os

username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip()
password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "").strip()

if not (email and password):
    raise SystemExit(0)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.filter(email=email).first()
if user is None:
    create_kwargs = {"email": email, "password": password}
    if username:
        create_kwargs["username"] = username
    User.objects.create_superuser(**create_kwargs)
else:
    # Ensure it is superuser/staff and password matches env
    if not user.is_staff:
        user.is_staff = True
    if not user.is_superuser:
        user.is_superuser = True
    if hasattr(user, "email_verified") and not user.email_verified:
        user.email_verified = True
    user.email = email
    user.set_password(password)
    user.save()
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
