# Interlabour Backend

This backend powers the Interlabour frontend with real Django APIs, authentication, admin workflows, and server-rendered pages.

## Quick Start

```bash
python -m venv .venv
```

Activate the virtual environment:

- Windows PowerShell:
```bash
.venv\Scripts\Activate.ps1
```

- macOS/Linux:
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Optional PostgreSQL extras:

```bash
pip install -r requirements-postgres.txt
```

Create the local environment file:

```bash
copy .env.example .env
```

Apply migrations and create an admin user:

```bash
python manage.py migrate
python manage.py createsuperuser
```

Start the development server:

```bash
python manage.py runserver
```

## What Is Tracked In Git

The repository is intended to track application code, templates, migrations, and deployment/config samples.

Local runtime artifacts are intentionally excluded from git:

- `.env`
- `db.sqlite3`
- `media/`
- `staticfiles/`
- virtual environments and Python cache files

## Frontend Inside Backend

Frontend files are available under `frontend/` and served directly by Django routes.

Examples:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/page-about.html`
- `http://127.0.0.1:8000/page-contact.html`
- `http://127.0.0.1:8000/pages/job-grid.html`
- `http://127.0.0.1:8000/login.html`
- `http://127.0.0.1:8000/register.html`
- `http://127.0.0.1:8000/verify-otp.html`

## Admin Dashboard

A custom admin dashboard is available at:

- `http://127.0.0.1:8000/dashboard/`

Access is restricted to admin-type users such as staff, superusers, or accounts with `user_type=admin`.

## API Base

Base URL:

- `http://127.0.0.1:8000/api/v1/`

Main endpoints include:

- `auth/register/`
- `auth/verify-email-otp/`
- `auth/resend-email-otp/`
- `auth/login/`
- `auth/refresh/`
- `auth/logout/`
- `auth/me/`
- `job-categories/`
- `companies/`
- `jobs/`
- `applications/`
- `candidates/`
- `blog-categories/`
- `blog-posts/`
- `services/`
- `contact-messages/`

## API Docs

- Schema JSON: `http://127.0.0.1:8000/api/schema/`
- Swagger UI: `http://127.0.0.1:8000/api/docs/swagger/`
- ReDoc: `http://127.0.0.1:8000/api/docs/redoc/`

## Authentication Flow

1. Register a user through `POST /api/v1/auth/register/`
2. Verify the email OTP through `POST /api/v1/auth/verify-email-otp/`
3. Log in through `POST /api/v1/auth/login/`
4. Refresh tokens through `POST /api/v1/auth/refresh/`
5. Fetch the current user through `GET /api/v1/auth/me/`

If SMTP credentials are configured in `.env`, OTP mail is sent through the configured provider. Otherwise, development fallback behavior may print the OTP locally.

## Database Setup

SQLite is the default for local development. Leave `DATABASE_URL` empty in `.env`.

For PostgreSQL, set:

```env
DATABASE_URL=postgres://db_user:db_password@127.0.0.1:5432/inter_labour
```

Then run:

```bash
python manage.py migrate
```
