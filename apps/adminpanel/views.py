import zipfile
from io import BytesIO
from pathlib import Path

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import FileResponse, Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.utils.translation import get_language as django_get_language
from django.utils.translation import gettext as _

from apps.accounts.permissions import is_admin_user
from apps.applications.models import Application
from apps.applications.emailing import send_application_status_update_email
from apps.content.models import BlogCategory, BlogPost, Partner, Service, Testimonial
from apps.jobs.models import ExperienceLevel, Job, JobCategory, JobType

from .forms import (
    ApplicationStatusForm,
    BlogCategoryForm,
    BlogPostForm,
    CategoryForm,
    ExperienceLevelForm,
    JobForm,
    JobTypeForm,
    PartnerForm,
    ServiceForm,
    TestimonialForm,
    normalize_admin_edit_lang,
)


def _admin_edit_lang(request: HttpRequest) -> str:
    return normalize_admin_edit_lang(getattr(request, "LANGUAGE_CODE", None) or django_get_language())


def admin_login(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated and is_admin_user(request.user):
        return redirect("adminpanel-dashboard")

    if request.method == "POST":
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user is None or not is_admin_user(user):
            messages.error(request, _("Invalid credentials."))
        else:
            login(request, user)
            return redirect("adminpanel-dashboard")

    return render(request, "adminpanel/login.html", {})


def admin_logout(request: HttpRequest) -> HttpResponse:
    logout(request)
    # The `?logout=1` flag tells auth-integration.js to wipe localStorage
    # tokens so the frontend nav shows Login/Register, not My Account/Logout.
    return redirect("/?logout=1")


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def dashboard(request: HttpRequest) -> HttpResponse:
    context = {
        "jobs_count": Job.objects.count(),
        "categories_count": JobCategory.objects.count(),
        "applications_count": Application.objects.count(),
        "services_count": Service.objects.count(),
        "blog_posts_count": BlogPost.objects.count(),
        "pending_testimonials_count": Testimonial.objects.filter(is_active=False).count(),
        "recent_applications": Application.objects.select_related("job", "applicant").order_by("-applied_at")[:20],
    }
    return render(request, "adminpanel/dashboard.html", context)


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def job_list(request: HttpRequest) -> HttpResponse:
    jobs = Job.objects.select_related("company", "category", "job_type_ref", "experience_level_ref").order_by("-posted_at")
    return render(request, "adminpanel/job_list.html", {"jobs": jobs})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def job_create(request: HttpRequest) -> HttpResponse:
    form = JobForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Job created."))
        return redirect("adminpanel-jobs")
    return render(request, "adminpanel/form.html", {"form": form, "title": _("Create job"), "multipart": True})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def job_edit(request: HttpRequest, job_id: int) -> HttpResponse:
    job = get_object_or_404(Job, id=job_id)
    form = JobForm(request.POST or None, request.FILES or None, instance=job)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Job updated."))
        return redirect("adminpanel-jobs")
    return render(request, "adminpanel/form.html", {"form": form, "title": _("Edit job"), "multipart": True})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def job_delete(request: HttpRequest, job_id: int) -> HttpResponse:
    job = get_object_or_404(Job, id=job_id)
    if request.method == "POST":
        job.delete()
        messages.success(request, _("Job deleted."))
        return redirect("adminpanel-jobs")
    return render(request, "adminpanel/confirm_delete.html", {"object": job, "title": _("Delete job")})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def category_list(request: HttpRequest) -> HttpResponse:
    categories = JobCategory.objects.order_by("name")
    return render(request, "adminpanel/category_list.html", {"categories": categories})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def category_create(request: HttpRequest) -> HttpResponse:
    form = CategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Category created."))
        return redirect("adminpanel-categories")
    return render(request, "adminpanel/form.html", {"form": form, "title": _("Create category")})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def category_edit(request: HttpRequest, category_id: int) -> HttpResponse:
    category = get_object_or_404(JobCategory, id=category_id)
    form = CategoryForm(request.POST or None, instance=category)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Category updated."))
        return redirect("adminpanel-categories")
    return render(request, "adminpanel/form.html", {"form": form, "title": _("Edit category")})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def category_delete(request: HttpRequest, category_id: int) -> HttpResponse:
    category = get_object_or_404(JobCategory, id=category_id)
    if request.method == "POST":
        category.delete()
        messages.success(request, _("Category deleted."))
        return redirect("adminpanel-categories")
    return render(request, "adminpanel/confirm_delete.html", {"object": category, "title": _("Delete category")})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def job_type_list(request: HttpRequest) -> HttpResponse:
    items = JobType.objects.order_by("name_en")
    return render(request, "adminpanel/job_type_list.html", {"items": items})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def job_type_create(request: HttpRequest) -> HttpResponse:
    form = JobTypeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Job type created."))
        return redirect("adminpanel-job-types")
    return render(request, "adminpanel/form.html", {"form": form, "title": _("Create job type")})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def job_type_edit(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(JobType, id=item_id)
    form = JobTypeForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Job type updated."))
        return redirect("adminpanel-job-types")
    return render(request, "adminpanel/form.html", {"form": form, "title": _("Edit job type")})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def job_type_delete(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(JobType, id=item_id)
    if request.method == "POST":
        item.delete()
        messages.success(request, _("Job type deleted."))
        return redirect("adminpanel-job-types")
    return render(request, "adminpanel/confirm_delete.html", {"object": item, "title": _("Delete job type")})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def experience_level_list(request: HttpRequest) -> HttpResponse:
    items = ExperienceLevel.objects.order_by("name_en")
    return render(request, "adminpanel/experience_level_list.html", {"items": items})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def experience_level_create(request: HttpRequest) -> HttpResponse:
    form = ExperienceLevelForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Experience level created."))
        return redirect("adminpanel-experience-levels")
    return render(request, "adminpanel/form.html", {"form": form, "title": _("Create experience level")})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def experience_level_edit(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(ExperienceLevel, id=item_id)
    form = ExperienceLevelForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Experience level updated."))
        return redirect("adminpanel-experience-levels")
    return render(request, "adminpanel/form.html", {"form": form, "title": _("Edit experience level")})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def experience_level_delete(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(ExperienceLevel, id=item_id)
    if request.method == "POST":
        item.delete()
        messages.success(request, _("Experience level deleted."))
        return redirect("adminpanel-experience-levels")
    return render(request, "adminpanel/confirm_delete.html", {"object": item, "title": _("Delete experience level")})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def application_list(request: HttpRequest) -> HttpResponse:
    qs = Application.objects.select_related("job", "job__company", "applicant").order_by("-applied_at")

    q = (request.GET.get("q") or "").strip()
    status = (request.GET.get("status") or "").strip()

    if q:
        from django.db.models import Q

        qs = qs.filter(
            Q(full_name__icontains=q)
            | Q(email__icontains=q)
            | Q(phone__icontains=q)
            | Q(job__title__icontains=q)
            | Q(job__title_en__icontains=q)
            | Q(job__title_nl__icontains=q)
        )
    if status:
        qs = qs.filter(status=status)

    return render(
        request,
        "adminpanel/application_list.html",
        {"applications": qs[:200], "q": q, "status": status},
    )


# ---------------------------------------------------------------------------
# Services CRUD
# ---------------------------------------------------------------------------

@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def service_list(request: HttpRequest) -> HttpResponse:
    services = Service.objects.order_by("display_order", "name")
    return render(request, "adminpanel/service_list.html", {"services": services})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def service_create(request: HttpRequest) -> HttpResponse:
    form = ServiceForm(
        request.POST or None, request.FILES or None, edit_lang=_admin_edit_lang(request)
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Service created."))
        return redirect("adminpanel-services")
    return render(
        request,
        "adminpanel/form.html",
        {
            "form": form,
            "title": _("Create service"),
            "multipart": True,
            "form_single_column": True,
        },
    )


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def service_edit(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(Service, id=item_id)
    form = ServiceForm(
        request.POST or None,
        request.FILES or None,
        instance=item,
        edit_lang=_admin_edit_lang(request),
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Service updated."))
        return redirect("adminpanel-services")
    return render(
        request,
        "adminpanel/form.html",
        {
            "form": form,
            "title": _("Edit service"),
            "multipart": True,
            "form_single_column": True,
        },
    )


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def service_delete(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(Service, id=item_id)
    if request.method == "POST":
        item.delete()
        messages.success(request, _("Service deleted."))
        return redirect("adminpanel-services")
    return render(request, "adminpanel/confirm_delete.html", {"object": item, "title": _("Delete service")})


# ---------------------------------------------------------------------------
# Blog posts CRUD
# ---------------------------------------------------------------------------

@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def blog_post_list(request: HttpRequest) -> HttpResponse:
    posts = BlogPost.objects.select_related("category").order_by("-published_at")
    return render(request, "adminpanel/blog_post_list.html", {"posts": posts})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def blog_post_create(request: HttpRequest) -> HttpResponse:
    form = BlogPostForm(
        request.POST or None, request.FILES or None, edit_lang=_admin_edit_lang(request)
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Blog post created."))
        return redirect("adminpanel-blog-posts")
    return render(
        request,
        "adminpanel/form.html",
        {
            "form": form,
            "title": _("Create blog post"),
            "multipart": True,
            "form_single_column": True,
        },
    )


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def blog_post_edit(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(BlogPost, id=item_id)
    form = BlogPostForm(
        request.POST or None,
        request.FILES or None,
        instance=item,
        edit_lang=_admin_edit_lang(request),
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Blog post updated."))
        return redirect("adminpanel-blog-posts")
    return render(
        request,
        "adminpanel/form.html",
        {
            "form": form,
            "title": _("Edit blog post"),
            "multipart": True,
            "form_single_column": True,
        },
    )


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def blog_post_delete(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(BlogPost, id=item_id)
    if request.method == "POST":
        item.delete()
        messages.success(request, _("Blog post deleted."))
        return redirect("adminpanel-blog-posts")
    return render(request, "adminpanel/confirm_delete.html", {"object": item, "title": _("Delete blog post")})


# ---------------------------------------------------------------------------
# Blog categories CRUD
# ---------------------------------------------------------------------------

@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def blog_category_list(request: HttpRequest) -> HttpResponse:
    categories = BlogCategory.objects.order_by("name")
    return render(request, "adminpanel/blog_category_list.html", {"categories": categories})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def blog_category_create(request: HttpRequest) -> HttpResponse:
    form = BlogCategoryForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Blog category created."))
        return redirect("adminpanel-blog-categories")
    return render(request, "adminpanel/form.html", {"form": form, "title": _("Create blog category")})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def blog_category_edit(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(BlogCategory, id=item_id)
    form = BlogCategoryForm(request.POST or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Blog category updated."))
        return redirect("adminpanel-blog-categories")
    return render(request, "adminpanel/form.html", {"form": form, "title": _("Edit blog category")})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def blog_category_delete(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(BlogCategory, id=item_id)
    if request.method == "POST":
        item.delete()
        messages.success(request, _("Blog category deleted."))
        return redirect("adminpanel-blog-categories")
    return render(request, "adminpanel/confirm_delete.html", {"object": item, "title": _("Delete blog category")})


# ---------------------------------------------------------------------------
# Testimonials CRUD
# ---------------------------------------------------------------------------

@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def testimonial_list(request: HttpRequest) -> HttpResponse:
    # Pending (user-submitted, awaiting moderation) first; then by order/recency
    items = Testimonial.objects.order_by("is_active", "display_order", "-created_at")
    pending_count = Testimonial.objects.filter(is_active=False).count()
    return render(
        request,
        "adminpanel/testimonial_list.html",
        {"items": items, "pending_count": pending_count},
    )


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def testimonial_approve(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(Testimonial, id=item_id)
    if request.method == "POST":
        item.is_active = True
        item.save(update_fields=["is_active", "updated_at"])
        messages.success(request, _("Testimonial approved and now visible on the website."))
    return redirect("adminpanel-testimonials")


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def testimonial_create(request: HttpRequest) -> HttpResponse:
    form = TestimonialForm(
        request.POST or None, request.FILES or None, edit_lang=_admin_edit_lang(request)
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Testimonial created."))
        return redirect("adminpanel-testimonials")
    return render(
        request,
        "adminpanel/form.html",
        {
            "form": form,
            "title": _("Create testimonial"),
            "multipart": True,
            "form_single_column": True,
        },
    )


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def testimonial_edit(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(Testimonial, id=item_id)
    form = TestimonialForm(
        request.POST or None,
        request.FILES or None,
        instance=item,
        edit_lang=_admin_edit_lang(request),
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Testimonial updated."))
        return redirect("adminpanel-testimonials")
    return render(
        request,
        "adminpanel/form.html",
        {
            "form": form,
            "title": _("Edit testimonial"),
            "multipart": True,
            "form_single_column": True,
        },
    )


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def testimonial_delete(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(Testimonial, id=item_id)
    if request.method == "POST":
        item.delete()
        messages.success(request, _("Testimonial deleted."))
        return redirect("adminpanel-testimonials")
    return render(request, "adminpanel/confirm_delete.html", {"object": item, "title": _("Delete testimonial")})


# ---------------------------------------------------------------------------
# Partners (client logos) CRUD
# ---------------------------------------------------------------------------

@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def partner_list(request: HttpRequest) -> HttpResponse:
    items = Partner.objects.order_by("display_order", "name")
    return render(request, "adminpanel/partner_list.html", {"items": items})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def partner_create(request: HttpRequest) -> HttpResponse:
    form = PartnerForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Partner created."))
        return redirect("adminpanel-partners")
    return render(request, "adminpanel/form.html", {"form": form, "title": _("Create partner"), "multipart": True})


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def partner_edit(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(Partner, id=item_id)
    form = PartnerForm(request.POST or None, request.FILES or None, instance=item)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, _("Partner updated."))
        return redirect("adminpanel-partners")
    return render(
        request,
        "adminpanel/form.html",
        {
            "form": form,
            "title": _("Edit partner"),
            "multipart": True,
            "form_single_column": True,
        },
    )


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def partner_delete(request: HttpRequest, item_id: int) -> HttpResponse:
    item = get_object_or_404(Partner, id=item_id)
    if request.method == "POST":
        item.delete()
        messages.success(request, _("Partner deleted."))
        return redirect("adminpanel-partners")
    return render(request, "adminpanel/confirm_delete.html", {"object": item, "title": _("Delete partner")})


_APPLICATION_DOC_FIELDS = {
    "aadhaar": "aadhaar_card",
    "pan": "pan_card",
    "passport": "passport",
    "resume": "resume",
}


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def application_serve_document(request: HttpRequest, app_id: int, kind: str, *, as_attachment: bool) -> FileResponse:
    """Serve one uploaded file: view (inline) or download — admin-only, no public /media/ needed."""
    app = get_object_or_404(Application.objects.select_related("job"), pk=app_id)
    field_name = _APPLICATION_DOC_FIELDS.get((kind or "").strip().lower())
    if not field_name:
        raise Http404(_("Unknown document type."))
    ff = getattr(app, field_name)
    if not ff or not ff.name:
        raise Http404(_("File not available."))
    try:
        fh = ff.open("rb")
    except FileNotFoundError as exc:
        raise Http404(_("File missing on server.")) from exc
    base = Path(ff.name).name
    cand = slugify(app.full_name) or "candidate"
    filename = f"{cand}_{kind}{Path(base).suffix.lower()}"
    return FileResponse(fh, as_attachment=as_attachment, filename=filename)


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def application_download_all_documents(request: HttpRequest, app_id: int) -> HttpResponse:
    """ZIP of all uploads for one application — admin-only."""
    app = get_object_or_404(Application.objects.select_related("job"), pk=app_id)
    cand = slugify(app.full_name) or "candidate"
    label_by_field = [
        ("aadhaar_card", "aadhaar"),
        ("pan_card", "pan"),
        ("passport", "passport"),
        ("resume", "resume"),
    ]
    buf = BytesIO()
    added = 0
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for field_name, label in label_by_field:
            ff = getattr(app, field_name)
            if not ff or not ff.name:
                continue
            try:
                with ff.open("rb") as fh:
                    data = fh.read()
            except FileNotFoundError:
                continue
            base = Path(ff.name).name
            arc = f"{label}_{cand}{Path(base).suffix.lower()}"
            zf.writestr(arc, data)
            added += 1
    if added == 0:
        raise Http404(_("No uploaded documents for this application."))
    fname = f"application-{app.pk}_{cand}_documents.zip".replace('"', "")
    resp = HttpResponse(buf.getvalue(), content_type="application/zip")
    resp["Content-Disposition"] = f'attachment; filename="{fname}"'
    return resp


@login_required(login_url="/adminpanel/login/")
@user_passes_test(is_admin_user, login_url="/adminpanel/login/")
def application_update_status(request: HttpRequest, app_id: int) -> HttpResponse:
    app = get_object_or_404(Application.objects.select_related("job", "applicant"), id=app_id)
    old_status = app.status
    form = ApplicationStatusForm(request.POST or None, instance=app)
    if request.method == "POST" and form.is_valid():
        updated = form.save()
        try:
            send_application_status_update_email(updated, old_status=old_status, new_status=updated.status)
        except Exception as exc:
            messages.warning(
                request,
                _("Status updated, but the email could not be sent. %(error)s") % {"error": str(exc)},
            )
        messages.success(request, _("Application status updated."))
        return redirect("adminpanel-applications")
    return render(request, "adminpanel/form.html", {"form": form, "title": _("Update application status")})

