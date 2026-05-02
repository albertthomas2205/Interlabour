#!/usr/bin/env sh
set -eu

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Optional: create a superuser non-interactively (only if env vars are set).
# Set these in Render Environment:
# - DJANGO_SUPERUSER_USERNAME
# - DJANGO_SUPERUSER_EMAIL
# - DJANGO_SUPERUSER_PASSWORD
python - <<'PY'
import os

username = os.getenv("DJANGO_SUPERUSER_USERNAME", "").strip()
email = os.getenv("DJANGO_SUPERUSER_EMAIL", "").strip()
password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "").strip()

if not (username and email and password):
    raise SystemExit(0)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.filter(username=username).first()
if user is None:
    User.objects.create_superuser(username=username, email=email, password=password)
else:
    # Ensure it is superuser/staff and password matches env
    changed = False
    if not user.is_staff:
        user.is_staff = True
        changed = True
    if not user.is_superuser:
        user.is_superuser = True
        changed = True
    user.email = email
    user.set_password(password)
    user.save()
PY

PORT="${PORT:-10000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"
GUNICORN_THREADS="${GUNICORN_THREADS:-4}"
GUNICORN_TIMEOUT="${GUNICORN_TIMEOUT:-120}"

exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY}" \
  --threads "${GUNICORN_THREADS}" \
  --timeout "${GUNICORN_TIMEOUT}"
