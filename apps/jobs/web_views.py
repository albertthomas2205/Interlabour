import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.translation import gettext as _

from apps.applications.models import Application
from apps.applications.emailing import send_application_submitted_email

from .emailing import send_job_alert_subscription_confirmation_email
from .forms import JobApplicationForm
from .models import ExperienceLevel, Job, JobAlertSubscription, JobCategory, JobType

logger = logging.getLogger(__name__)

_ALLOWED_SUBSCRIBE_NEXT = frozenset({"/jobs/", "/page-contact.html", "/pages/page-contact.html"})


def job_alert_confirmed(request):
    """Public landing page for the 'Translate' button in email clients."""
    email = (request.GET.get("email") or "").strip().lower()
    lang = (request.GET.get("lang") or "nl").split("-")[0].lower()
    if lang not in ("nl", "en"):
        lang = "nl"

    # Keep this page non-sensitive; we don't expose subscription state here.
    site = (getattr(request, "build_absolute_uri", None) and request.build_absolute_uri("/")) or ""
    site = site.rstrip("/")
    jobs_url = f"{site}/jobs/" if site else "/jobs/"

    toggle_lang = "en" if lang == "nl" else "nl"
    base = "/jobs/alerts/confirmed/"
    toggle_url = f"{base}?email={email}&lang={toggle_lang}" if email else f"{base}?lang={toggle_lang}"
    context = {
        "email": email,
        "lang": lang,
        "toggle_url": toggle_url,
        "jobs_url": jobs_url,
        "site_url": site,
    }
    return render(request, "frontend/job_alert_subscription_confirmed.html", context)


def job_list(request):
    jobs = Job.objects.filter(is_active=True).select_related("company", "category").order_by("-posted_at")

    # Optional sidebar filters
    category_id    = request.GET.get("category")
    job_type_id    = request.GET.get("job_type")
    experience_id  = request.GET.get("experience")

    if category_id:
        jobs = jobs.filter(category__id=category_id)
    if job_type_id:
        jobs = jobs.filter(job_type_ref__id=job_type_id)
    if experience_id:
        jobs = jobs.filter(experience_level_ref__id=experience_id)

    jobs = jobs[:50]

    return render(request, "frontend/job-list.html", {
        "jobs":              jobs,
        "categories":        JobCategory.objects.all().order_by("name"),
        "job_types":         JobType.objects.all().order_by("name_en"),
        "experience_levels": ExperienceLevel.objects.all().order_by("name_en"),
    })


@csrf_exempt
@require_POST
def job_alert_subscribe(request):
    email = (request.POST.get("email") or "").strip().lower()
    next_path = (request.POST.get("next") or "").strip()
    if next_path not in _ALLOWED_SUBSCRIBE_NEXT:
        next_path = "/jobs/"

    if not email or "@" not in email:
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"ok": False, "error": _("Please enter a valid email address.")}, status=400)
        return redirect(f"{next_path}?subscribed=0")

    lang = (getattr(request, "LANGUAGE_CODE", None) or "nl").split("-")[0].lower()
    if lang not in ("nl", "en"):
        lang = "nl"

    sub, created = JobAlertSubscription.objects.get_or_create(
        email=email,
        defaults={"language": lang, "is_active": True},
    )
    if not created:
        changed = False
        if not sub.is_active:
            sub.is_active = True
            changed = True
        if sub.language != lang:
            sub.language = lang
            changed = True
        if changed:
            sub.save(update_fields=["language", "is_active", "updated_at"])

    try:
        send_job_alert_subscription_confirmation_email(email, language_code=lang)
    except Exception:
        logger.exception("Job alert subscribe saved but confirmation email failed for %s", email)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True})
    return redirect(f"{next_path}?subscribed=1")


def job_detail(request, slug: str):
    job = get_object_or_404(
        Job.objects.select_related("company", "category", "job_type_ref", "experience_level_ref"),
        slug=slug,
        is_active=True,
    )
    recent_jobs = (
        Job.objects.filter(is_active=True)
        .exclude(id=job.id)
        .select_related("company", "category")
        .order_by("-posted_at")[:6]
    )
    return render(request, "frontend/job-single.html", {"job": job, "recent_jobs": recent_jobs})


def job_apply(request, slug: str):
    if not request.user.is_authenticated:
        return redirect(f"/login.html?next=/jobs/{slug}/apply/")

    job = get_object_or_404(Job.objects.select_related("company"), slug=slug, is_active=True)
    if Application.objects.filter(job=job, applicant=request.user).exists():
        messages.info(request, _("You have already applied to this job."))
        return redirect("user-account")

    initial = {
        "full_name": f"{request.user.first_name} {request.user.last_name}".strip(),
        "email": request.user.email,
    }
    form = JobApplicationForm(request.POST or None, request.FILES or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        application = form.save(commit=False)
        application.job       = job
        application.applicant = request.user
        application.status    = Application.ApplicationStatus.REVIEWING
        application.save()
        try:
            send_application_submitted_email(application)
        except Exception:
            pass
        messages.success(request, _("Application submitted successfully."))
        return redirect("user-account")

    return render(request, "frontend/job-apply.html", {"job": job, "form": form})
