from django import forms
from django.utils.translation import get_language
from django.utils.translation import gettext_lazy as _

from apps.applications.models import Application
from apps.content.models import BlogCategory, BlogPost, Partner, Service, Testimonial
from apps.jobs.models import Company, ExperienceLevel, Job, JobCategory, JobType


def normalize_admin_edit_lang(code: str | None) -> str:
    if not code:
        return "nl"
    c = str(code).split("-")[0].lower()
    return c if c in ("en", "nl") else "nl"


def _get_default_company() -> Company:
    """Fallback used only when the admin leaves the company name blank."""
    company = Company.objects.order_by("id").first()
    if company is None:
        company, _ = Company.objects.get_or_create(
            name="Inter Labour",
            defaults={"is_active": True},
        )
    return company


def _resolve_company(name: str) -> Company:
    """Resolve a company by name from the free-text input.

    Matching is case-insensitive on the trimmed name. If no company exists
    with that name, a new one is created on the fly so the admin never has
    to leave the job form to manage companies.
    """
    cleaned = (name or "").strip()
    if not cleaned:
        return _get_default_company()
    existing = Company.objects.filter(name__iexact=cleaned).order_by("id").first()
    if existing is not None:
        return existing
    return Company.objects.create(name=cleaned, is_active=True)


class CategoryForm(forms.ModelForm):
    """Single-input category form. The same value is mirrored across name/_en/_nl
    so existing multilingual lookups keep working without forcing the admin to
    fill multiple language fields.
    """

    name = forms.CharField(label=_("Name"), max_length=120)
    description = forms.CharField(
        label=_("Description"), required=False, widget=forms.Textarea(attrs={"rows": 3})
    )

    class Meta:
        model = JobCategory
        fields = ["name", "description"]

    def save(self, commit: bool = True) -> JobCategory:
        instance: JobCategory = super().save(commit=False)
        name = self.cleaned_data.get("name", "").strip()
        description = self.cleaned_data.get("description", "")
        instance.name = name
        instance.name_en = name
        instance.name_nl = name
        instance.description = description
        instance.description_en = description
        instance.description_nl = description
        if commit:
            instance.save()
        return instance


class JobTypeForm(forms.ModelForm):
    name = forms.CharField(label=_("Name"), max_length=120)

    class Meta:
        model = JobType
        fields: list[str] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["name"].initial = self.instance.name_en or self.instance.name_nl

    def save(self, commit: bool = True) -> JobType:
        instance: JobType = super().save(commit=False)
        name = self.cleaned_data.get("name", "").strip()
        instance.name_en = name
        instance.name_nl = name
        if commit:
            instance.save()
        return instance


class ExperienceLevelForm(forms.ModelForm):
    name = forms.CharField(label=_("Name"), max_length=120)

    class Meta:
        model = ExperienceLevel
        fields: list[str] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["name"].initial = self.instance.name_en or self.instance.name_nl

    def save(self, commit: bool = True) -> ExperienceLevel:
        instance: ExperienceLevel = super().save(commit=False)
        name = self.cleaned_data.get("name", "").strip()
        instance.name_en = name
        instance.name_nl = name
        if commit:
            instance.save()
        return instance


class JobForm(forms.ModelForm):
    """Simplified job form.

    The admin only fills one Title / Description / Requirements / Responsibilities
    field — the same value is mirrored into the *_en / *_nl columns under the
    hood so the language-aware property accessors keep working.

    The Company field is rendered as a free-text input (no dropdown). On save
    we look up an existing company with that name (case-insensitive) or
    create a new one transparently.
    """

    company = forms.CharField(label=_("Company"), max_length=180, required=False)

    field_order = [
        "title",
        "image",
        "company",
        "category",
        "location",
        "job_type_ref",
        "experience_level_ref",
        "salary_min",
        "salary_max",
        "currency",
        "description",
        "responsibilities",
        "requirements",
        "benefits",
        "deadline",
        "is_featured",
        "is_active",
    ]

    class Meta:
        model = Job
        fields = [
            "title",
            "image",
            "category",
            "location",
            "job_type_ref",
            "experience_level_ref",
            "salary_min",
            "salary_max",
            "currency",
            "description",
            "responsibilities",
            "requirements",
            "benefits",
            "deadline",
            "is_featured",
            "is_active",
        ]
        labels = {
            "title": _("Title"),
            "image": _("Picture"),
            "category": _("Category"),
            "location": _("Location"),
            "job_type_ref": _("Job type"),
            "experience_level_ref": _("Experience level"),
            "salary_min": _("Salary min"),
            "salary_max": _("Salary max"),
            "currency": _("Currency"),
            "description": _("Description"),
            "responsibilities": _("Key responsibilities"),
            "requirements": _("Requirements"),
            "benefits": _("Benefits"),
            "deadline": _("Deadline"),
            "is_featured": _("Is featured"),
            "is_active": _("Is active"),
        }
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 4, "placeholder": _("Short description shown on the listing and detail pages.")}),
            "responsibilities": forms.Textarea(attrs={"rows": 5, "placeholder": _("One responsibility per line, e.g.\nPlanten, verzorgen en oogsten van gewassen\nSorteren en verpakken van producten")}),
            "requirements": forms.Textarea(attrs={"rows": 4, "placeholder": _("One requirement per line, e.g.\nGoede fysieke conditie\nFlexibel en gemotiveerd")}),
            "benefits": forms.Textarea(attrs={"rows": 4, "placeholder": _("One benefit per line, e.g.\nCompetitief salaris\nHuisvesting (indien van toepassing)")}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.company_id:
            self.fields["company"].initial = self.instance.company.name

    def save(self, commit: bool = True) -> Job:
        instance: Job = super().save(commit=False)
        title = (self.cleaned_data.get("title") or "").strip()
        description = self.cleaned_data.get("description") or ""
        requirements = self.cleaned_data.get("requirements") or ""
        responsibilities = self.cleaned_data.get("responsibilities") or ""

        instance.title = title
        instance.title_en = title
        instance.title_nl = title

        instance.description = description
        instance.description_en = description
        instance.description_nl = description

        instance.requirements = requirements
        instance.requirements_en = requirements
        instance.requirements_nl = requirements

        instance.responsibilities = responsibilities
        instance.responsibilities_en = responsibilities
        instance.responsibilities_nl = responsibilities

        benefits = self.cleaned_data.get("benefits") or ""
        instance.benefits = benefits
        instance.benefits_en = benefits
        instance.benefits_nl = benefits

        # Resolve the free-text Company input (no dropdown).
        company_name = (self.cleaned_data.get("company") or "").strip()
        if company_name:
            instance.company = _resolve_company(company_name)
        elif not getattr(instance, "company_id", None):
            instance.company = _get_default_company()

        # Keep legacy text choice fields in sync with FK selections
        if instance.job_type_ref_id:
            instance.job_type = (instance.job_type_ref.name_en or instance.job_type or "").lower().replace(" ", "_")[:20] or instance.job_type
        if instance.experience_level_ref_id:
            instance.experience_level = (instance.experience_level_ref.name_en or instance.experience_level or "").lower().replace(" ", "_")[:20] or instance.experience_level

        if commit:
            instance.save()
        return instance


class ApplicationStatusForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ["status"]


class ServiceForm(forms.ModelForm):
    """One field per concept; stores into *_en or *_nl based on ``edit_lang`` (admin UI language)."""

    name = forms.CharField(label=_("Name"), max_length=180)
    short_description = forms.CharField(
        label=_("Short description"), max_length=300, required=False, widget=forms.TextInput()
    )
    details = forms.CharField(
        label=_("Details"),
        required=False,
        widget=forms.Textarea(attrs={"rows": 5}),
    )

    field_order = [
        "name",
        "short_description",
        "details",
        "image",
        "icon_name",
        "display_order",
        "is_active",
    ]

    class Meta:
        model = Service
        fields = ["image", "icon_name", "display_order", "is_active"]
        labels = {
            "image": _("Image"),
            "icon_name": _("Icon name (optional)"),
            "display_order": _("Display order"),
            "is_active": _("Is active"),
        }

    def __init__(self, *args, edit_lang: str | None = None, **kwargs):
        self._edit_lang = normalize_admin_edit_lang(edit_lang or get_language())
        super().__init__(*args, **kwargs)

        suf = "_en" if self._edit_lang == "en" else "_nl"
        inst = self.instance
        if inst and inst.pk:
            self.fields["name"].initial = (
                getattr(inst, f"name{suf}") or inst.name_nl or inst.name_en or inst.name or ""
            )
            self.fields["short_description"].initial = (
                getattr(inst, f"short_description{suf}") or inst.short_description_nl or inst.short_description_en or inst.short_description or ""
            )
            self.fields["details"].initial = (
                getattr(inst, f"details{suf}") or inst.details_nl or inst.details_en or inst.details or ""
            )

    def save(self, commit=True):
        instance: Service = super().save(commit=False)
        name = (self.cleaned_data.get("name") or "").strip()
        short_desc = (self.cleaned_data.get("short_description") or "").strip()
        details = self.cleaned_data.get("details") or ""

        if self._edit_lang == "en":
            instance.name_en = name
            instance.short_description_en = short_desc
            instance.details_en = details
        else:
            instance.name_nl = name
            instance.short_description_nl = short_desc
            instance.details_nl = details

        instance.name = (instance.name_en or instance.name_nl or name).strip()
        instance.short_description = (
            instance.short_description_en or instance.short_description_nl or short_desc
        ).strip()
        instance.details = (instance.details_en or instance.details_nl or details).strip()

        if commit:
            instance.save()
        return instance


class BlogCategoryForm(forms.ModelForm):
    name = forms.CharField(label=_("Name"), max_length=120)

    class Meta:
        model = BlogCategory
        fields: list[str] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["name"].initial = self.instance.name_en or self.instance.name_nl or self.instance.name

    def save(self, commit=True):
        instance: BlogCategory = super().save(commit=False)
        name = (self.cleaned_data.get("name") or "").strip()
        instance.name = name
        instance.name_en = name
        instance.name_nl = name
        if commit:
            instance.save()
        return instance


class BlogPostForm(forms.ModelForm):
    """One field per concept; stores into *_en or *_nl based on ``edit_lang``."""

    title = forms.CharField(label=_("Title"), max_length=220)
    excerpt = forms.CharField(
        label=_("Excerpt"),
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
    )
    content = forms.CharField(
        label=_("Content"),
        widget=forms.Textarea(attrs={"rows": 12}),
    )

    field_order = [
        "title",
        "excerpt",
        "content",
        "author_name",
        "featured_image",
        "featured_image_url",
        "is_published",
        "published_at",
    ]

    class Meta:
        model = BlogPost
        fields = [
            "author_name",
            "featured_image",
            "featured_image_url",
            "is_published",
            "published_at",
        ]
        labels = {
            "author_name": _("Author"),
            "featured_image": _("Featured image"),
            "featured_image_url": _("Featured image URL (optional)"),
            "is_published": _("Is published"),
            "published_at": _("Published at"),
        }
        widgets = {"published_at": forms.DateTimeInput(attrs={"type": "datetime-local"})}

    def __init__(self, *args, edit_lang: str | None = None, **kwargs):
        self._edit_lang = normalize_admin_edit_lang(edit_lang or get_language())
        super().__init__(*args, **kwargs)

        suf = "_en" if self._edit_lang == "en" else "_nl"
        inst = self.instance
        if inst and inst.pk:
            self.fields["title"].initial = (
                getattr(inst, f"title{suf}") or inst.title_nl or inst.title_en or inst.title or ""
            )
            self.fields["excerpt"].initial = (
                getattr(inst, f"excerpt{suf}") or inst.excerpt_nl or inst.excerpt_en or inst.excerpt or ""
            )
            self.fields["content"].initial = (
                getattr(inst, f"content{suf}") or inst.content_nl or inst.content_en or inst.content or ""
            )

    def save(self, commit=True):
        instance: BlogPost = super().save(commit=False)
        title = (self.cleaned_data.get("title") or "").strip()
        excerpt = self.cleaned_data.get("excerpt") or ""
        content = self.cleaned_data.get("content") or ""

        if self._edit_lang == "en":
            instance.title_en = title
            instance.excerpt_en = excerpt
            instance.content_en = content
        else:
            instance.title_nl = title
            instance.excerpt_nl = excerpt
            instance.content_nl = content

        instance.title = (instance.title_en or instance.title_nl or title).strip()
        instance.excerpt = (instance.excerpt_en or instance.excerpt_nl or excerpt).strip()
        instance.content = (instance.content_en or instance.content_nl or content).strip()

        if commit:
            instance.save()
        return instance


class TestimonialForm(forms.ModelForm):
    """Role + quote use one field each; language-specific columns follow ``edit_lang``."""

    author_role = forms.CharField(
        label=_("Role / company"),
        max_length=180,
        required=False,
        help_text=_("e.g. Operations Manager, Acme Corp"),
    )
    message = forms.CharField(
        label=_("Quote"),
        widget=forms.Textarea(attrs={"rows": 5}),
    )

    field_order = [
        "author_name",
        "author_role",
        "message",
        "photo",
        "rating",
        "display_order",
        "is_active",
    ]

    class Meta:
        model = Testimonial
        fields = ["author_name", "photo", "rating", "display_order", "is_active"]
        labels = {
            "author_name": _("Client name"),
            "photo": _("Photo"),
            "rating": _("Rating (1–5)"),
            "display_order": _("Display order"),
            "is_active": _("Is active"),
        }

    def __init__(self, *args, edit_lang: str | None = None, **kwargs):
        self._edit_lang = normalize_admin_edit_lang(edit_lang or get_language())
        super().__init__(*args, **kwargs)

        suf = "_en" if self._edit_lang == "en" else "_nl"
        inst = self.instance
        if inst and inst.pk:
            self.fields["author_role"].initial = (
                getattr(inst, f"author_role{suf}") or inst.author_role_nl or inst.author_role_en or inst.author_role or ""
            )
            self.fields["message"].initial = (
                getattr(inst, f"message{suf}") or inst.message_nl or inst.message_en or inst.message or ""
            )

    def save(self, commit=True):
        instance: Testimonial = super().save(commit=False)
        role = (self.cleaned_data.get("author_role") or "").strip()
        message = (self.cleaned_data.get("message") or "").strip()

        if self._edit_lang == "en":
            instance.author_role_en = role
            instance.message_en = message
        else:
            instance.author_role_nl = role
            instance.message_nl = message

        instance.author_role = (instance.author_role_en or instance.author_role_nl or role).strip()
        instance.message = (instance.message_en or instance.message_nl or message).strip()

        if commit:
            instance.save()
        return instance


class PartnerForm(forms.ModelForm):
    """Partner / client logo form."""

    class Meta:
        model = Partner
        fields = [
            "name",
            "logo",
            "logo_url",
            "website",
            "display_order",
            "is_active",
        ]
        labels = {
            "name": _("Company name"),
            "logo": _("Logo file (preferred)"),
            "logo_url": _("Logo URL (fallback)"),
            "website": _("Website URL"),
            "display_order": _("Display order"),
            "is_active": _("Is active"),
        }
