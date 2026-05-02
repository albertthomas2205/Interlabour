import mimetypes
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User
from apps.accounts.permissions import is_admin_user, is_company_user, is_normal_user
from apps.applications.models import Application
from apps.communication.models import ContactMessage
from apps.content.models import BlogPost, Service
from apps.jobs.forms import CompanyJobForm, CompanyProfileForm, JobApplicationForm
from apps.jobs.models import Company, Job
from apps.people.models import CandidateProfile


FRONTEND_DIR = settings.BASE_DIR / "frontend"
SUPPORTED_DASHBOARD_LANGUAGES = {"nl", "en"}

I18N = {
    "nl": {
        "dashboard": "Dashboard",
        "admin_dashboard": "Beheer Dashboard",
        "company_dashboard": "Bedrijf Dashboard",
        "user_dashboard": "Gebruiker Dashboard",
        "users": "Gebruikers",
        "jobs": "Vacatures",
        "companies": "Bedrijven",
        "applications": "Sollicitaties",
        "candidates": "Kandidaten",
        "services": "Diensten",
        "blog_posts": "Blog Berichten",
        "messages": "Berichten",
        "my_company": "Mijn Bedrijf",
        "my_jobs": "Mijn Vacatures",
        "active_jobs": "Actieve Vacatures",
        "new_applications": "Nieuwe Sollicitaties",
        "my_applications": "Mijn Sollicitaties",
        "shortlisted": "Op shortlist",
        "hired": "Aangenomen",
        "available_jobs": "Beschikbare Vacatures",
        "recent_jobs": "Recente Vacatures",
        "recent_applications": "Recente Sollicitaties",
        "post_job": "Vacature Plaatsen",
        "edit_company": "Bedrijf Bewerken",
        "create_company": "Bedrijf Aanmaken",
        "view_jobs": "Vacatures Bekijken",
        "apply_now": "Nu Solliciteren",
        "logout": "Uitloggen",
        "api_docs": "API Documentatie",
        "django_admin": "Django Admin",
        "frontend_home": "Frontend Home",
        "language": "Taal",
        "dutch": "Nederlands",
        "english": "Engels",
        "no_company_profile": "Nog geen bedrijfsprofiel. Maak eerst je profiel aan.",
        "job_post_success": "Vacature succesvol geplaatst.",
        "application_success": "Sollicitatie succesvol verzonden.",
        "already_applied": "Je hebt al op deze vacature gesolliciteerd.",
        "manage_profile": "Beheer bedrijfsprofiel",
        "company_profile": "Bedrijfsprofiel",
        "save": "Opslaan",
        "cancel": "Annuleren",
        "submit_application": "Sollicitatie Versturen",
        "select_job": "Kies vacature",
        "back_dashboard": "Terug naar dashboard",
        "no_records": "Geen records gevonden.",
        "quick_actions": "Snelle acties",
    },
    "en": {
        "dashboard": "Dashboard",
        "admin_dashboard": "Admin Dashboard",
        "company_dashboard": "Company Dashboard",
        "user_dashboard": "User Dashboard",
        "users": "Users",
        "jobs": "Jobs",
        "companies": "Companies",
        "applications": "Applications",
        "candidates": "Candidates",
        "services": "Services",
        "blog_posts": "Blog Posts",
        "messages": "Messages",
        "my_company": "My Company",
        "my_jobs": "My Jobs",
        "active_jobs": "Active Jobs",
        "new_applications": "New Applications",
        "my_applications": "My Applications",
        "shortlisted": "Shortlisted",
        "hired": "Hired",
        "available_jobs": "Available Jobs",
        "recent_jobs": "Recent Jobs",
        "recent_applications": "Recent Applications",
        "post_job": "Post Job",
        "edit_company": "Edit Company",
        "create_company": "Create Company",
        "view_jobs": "Browse Jobs",
        "apply_now": "Apply Now",
        "logout": "Logout",
        "api_docs": "API Docs",
        "django_admin": "Django Admin",
        "frontend_home": "Frontend Home",
        "language": "Language",
        "dutch": "Dutch",
        "english": "English",
        "no_company_profile": "No company profile yet. Create your company profile first.",
        "job_post_success": "Job posted successfully.",
        "application_success": "Application submitted successfully.",
        "already_applied": "You have already applied to this job.",
        "manage_profile": "Manage company profile",
        "company_profile": "Company Profile",
        "save": "Save",
        "cancel": "Cancel",
        "submit_application": "Submit Application",
        "select_job": "Select job",
        "back_dashboard": "Back to dashboard",
        "no_records": "No records found.",
        "quick_actions": "Quick actions",
    },
}


def _resolve_frontend_path(page_path: str) -> Path:
    normalized = (page_path or "index.html").lstrip("/")

    if normalized.startswith("pages/assets/"):
        normalized = "assets/" + normalized[len("pages/assets/") :]

    target = FRONTEND_DIR / normalized
    if target.is_dir():
        target = target / "index.html"

    if not target.exists() and "." not in target.name:
        html_target = target.with_suffix(".html")
        if html_target.exists():
            target = html_target

    resolved = target.resolve()
    if FRONTEND_DIR.resolve() not in resolved.parents and resolved != FRONTEND_DIR.resolve():
        raise Http404("Invalid path.")
    if not resolved.exists() or not resolved.is_file():
        raise Http404("Page not found.")
    return resolved


def frontend_page(request, page_path="index.html"):
    file_path = _resolve_frontend_path(page_path)
    file_name = file_path.name.lower()
    if file_name.endswith(".js") or ".js@" in file_name:
        content_type = "application/javascript"
    elif file_name.endswith(".css") or ".css@" in file_name:
        content_type = "text/css"
    else:
        content_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
    return FileResponse(open(file_path, "rb"), content_type=content_type)


def get_dashboard_language(request):
    selected = request.GET.get("lang", "").lower().strip()
    if selected in SUPPORTED_DASHBOARD_LANGUAGES:
        request.session["dashboard_language"] = selected
        return selected
    session_value = request.session.get("dashboard_language")
    if session_value in SUPPORTED_DASHBOARD_LANGUAGES:
        return session_value
    return "nl"


def dashboard_context(request, title_key):
    lang = get_dashboard_language(request)
    text = I18N[lang]
    return {
        "lang": lang,
        "text": text,
        "title": text[title_key],
        "switch_to": "en" if lang == "nl" else "nl",
        "switch_label": text["english"] if lang == "nl" else text["dutch"],
    }


@login_required(login_url="/accounts/login/")
def dashboard_home(request):
    if is_admin_user(request.user):
        return redirect("adminpanel-dashboard")
    return redirect("user-account")


@login_required(login_url="/accounts/login/")
@user_passes_test(is_admin_user, login_url="/dashboard/")
def admin_dashboard(request):
    context = dashboard_context(request, "admin_dashboard")
    context.update(
        {
            "cards": [
                {"label": context["text"]["users"], "value": User.objects.count()},
                {"label": context["text"]["jobs"], "value": Job.objects.count()},
                {"label": context["text"]["companies"], "value": Company.objects.count()},
                {"label": context["text"]["applications"], "value": Application.objects.count()},
                {"label": context["text"]["candidates"], "value": CandidateProfile.objects.count()},
                {"label": context["text"]["services"], "value": Service.objects.count()},
                {"label": context["text"]["blog_posts"], "value": BlogPost.objects.count()},
                {"label": context["text"]["messages"], "value": ContactMessage.objects.count()},
            ]
        }
    )
    return render(request, "dashboard/admin.html", context)


@login_required(login_url="/accounts/login/")
@user_passes_test(is_company_user, login_url="/dashboard/")
def company_dashboard(request):
    context = dashboard_context(request, "company_dashboard")
    company = Company.objects.filter(owner=request.user).first()
    company_jobs = Job.objects.filter(company=company) if company else Job.objects.none()
    company_applications = Application.objects.filter(job__company=company) if company else Application.objects.none()
    context.update(
        {
            "company": company,
            "cards": [
                {"label": context["text"]["my_jobs"], "value": company_jobs.count()},
                {"label": context["text"]["active_jobs"], "value": company_jobs.filter(is_active=True).count()},
                {"label": context["text"]["applications"], "value": company_applications.count()},
                {
                    "label": context["text"]["new_applications"],
                    "value": company_applications.filter(
                        status=Application.ApplicationStatus.SUBMITTED
                    ).count(),
                },
            ],
            "recent_applications": company_applications.select_related("job")[:8],
        }
    )
    return render(request, "dashboard/company.html", context)


@login_required(login_url="/accounts/login/")
@user_passes_test(is_normal_user, login_url="/dashboard/")
def user_dashboard(request):
    context = dashboard_context(request, "user_dashboard")
    my_applications = Application.objects.filter(applicant=request.user)
    context.update(
        {
            "cards": [
                {"label": context["text"]["my_applications"], "value": my_applications.count()},
                {
                    "label": context["text"]["shortlisted"],
                    "value": my_applications.filter(status=Application.ApplicationStatus.SHORTLISTED).count(),
                },
                {"label": context["text"]["hired"], "value": my_applications.filter(status=Application.ApplicationStatus.HIRED).count()},
                {"label": context["text"]["available_jobs"], "value": Job.objects.filter(is_active=True).count()},
            ],
            "recent_jobs": Job.objects.filter(is_active=True).select_related("company", "category")[:8],
            "my_recent_applications": my_applications.select_related("job")[:8],
        }
    )
    return render(request, "dashboard/user.html", context)


@login_required(login_url="/accounts/login/")
@user_passes_test(is_company_user, login_url="/dashboard/")
def company_profile_manage(request):
    company = Company.objects.filter(owner=request.user).first()
    form = CompanyProfileForm(request.POST or None, instance=company)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.owner = request.user
        item.save()
        messages.success(request, "Profile saved.")
        return redirect("company-dashboard")

    context = dashboard_context(request, "company_profile")
    context.update({"form": form, "company": company})
    return render(request, "dashboard/company_profile_form.html", context)


@login_required(login_url="/accounts/login/")
@user_passes_test(is_company_user, login_url="/dashboard/")
def company_job_create(request):
    company = Company.objects.filter(owner=request.user).first()
    context = dashboard_context(request, "post_job")
    if not company:
        messages.warning(request, context["text"]["no_company_profile"])
        return redirect("company-profile-manage")

    form = CompanyJobForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        job = form.save(commit=False)
        job.company = company
        job.save()
        messages.success(request, context["text"]["job_post_success"])
        return redirect("company-dashboard")

    context.update({"form": form, "company": company})
    return render(request, "dashboard/job_form.html", context)


@login_required(login_url="/accounts/login/")
@user_passes_test(is_normal_user, login_url="/dashboard/")
def user_jobs(request):
    context = dashboard_context(request, "jobs")
    jobs = Job.objects.filter(is_active=True).select_related("company", "category")
    query = request.GET.get("q", "").strip()
    if query:
        jobs = jobs.filter(Q(title__icontains=query) | Q(location__icontains=query) | Q(company__name__icontains=query))
    context.update({"jobs": jobs[:50], "query": query})
    return render(request, "dashboard/job_list.html", context)


@login_required(login_url="/accounts/login/")
@user_passes_test(is_normal_user, login_url="/dashboard/")
def user_job_apply(request, job_id):
    job = get_object_or_404(Job.objects.select_related("company"), id=job_id, is_active=True)
    existing = Application.objects.filter(job=job, applicant=request.user).exists()
    context = dashboard_context(request, "submit_application")
    if existing:
        messages.info(request, context["text"]["already_applied"])
        return redirect("user-dashboard")

    initial = {
        "full_name": f"{request.user.first_name} {request.user.last_name}".strip(),
        "email": request.user.email,
    }
    form = JobApplicationForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        application = form.save(commit=False)
        application.job = job
        application.applicant = request.user
        application.save()
        messages.success(request, context["text"]["application_success"])
        return redirect("user-dashboard")

    context.update({"form": form, "job": job})
    return render(request, "dashboard/job_apply.html", context)
