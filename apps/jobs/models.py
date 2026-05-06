from django.conf import settings
from django.db import models
from django.utils.translation import get_language
from django.utils.text import slugify


def _generate_unique_slug_for_instance(*, instance: models.Model, base: str, slug_field_name: str = "slug") -> str:
    """
    Generate a unique slug for the instance's model (foo, foo-2, foo-3, ...).
    """
    base_slug = slugify(base) or instance.__class__.__name__.lower()

    field = instance._meta.get_field(slug_field_name)
    max_len = getattr(field, "max_length", None) or 220

    def _truncate(s: str, suffix: str = "") -> str:
        # Ensure final slug (s + suffix) fits max_len
        allowed = max_len - len(suffix)
        if allowed < 1:
            return suffix[-max_len:] or "x"
        return (s[:allowed]).rstrip("-") + suffix

    base_slug = _truncate(base_slug)
    slug = base_slug

    qs = instance.__class__.objects.all()
    if instance.pk:
        qs = qs.exclude(pk=instance.pk)

    i = 2
    while qs.filter(**{slug_field_name: slug}).exists():
        suffix = f"-{i}"
        slug = _truncate(base_slug, suffix)
        i += 1
    return slug


class JobAlertSubscription(models.Model):
    """Email-only job alerts when a new job is published."""

    class Language(models.TextChoices):
        NL = "nl", "Dutch"
        EN = "en", "English"

    email = models.EmailField(max_length=254, unique=True)
    language = models.CharField(max_length=5, choices=Language.choices, default=Language.NL)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email


class JobCategory(models.Model):
    # Legacy fields (kept for backwards compatibility / existing data)
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)
    description = models.TextField(blank=True)

    # Multilingual fields (preferred)
    name_en = models.CharField(max_length=120, blank=True, default="")
    name_nl = models.CharField(max_length=120, blank=True, default="")
    description_en = models.TextField(blank=True, default="")
    description_nl = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name_nl or self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.display_name

    @property
    def display_name(self) -> str:
        lang = (get_language() or "en").split("-")[0]
        if lang == "nl":
            return self.name_nl or self.name_en or self.name
        return self.name_en or self.name_nl or self.name


class JobType(models.Model):
    name_en = models.CharField(max_length=120, unique=True)
    name_nl = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        ordering = ["name_en"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name_nl)
        super().save(*args, **kwargs)

    @property
    def display_name(self) -> str:
        lang = (get_language() or "en").split("-")[0]
        if lang == "nl":
            return self.name_nl or self.name_en
        return self.name_en or self.name_nl

    def __str__(self) -> str:
        return self.display_name


class ExperienceLevel(models.Model):
    name_en = models.CharField(max_length=120, unique=True)
    name_nl = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        ordering = ["name_en"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name_nl)
        super().save(*args, **kwargs)

    @property
    def display_name(self) -> str:
        lang = (get_language() or "en").split("-")[0]
        if lang == "nl":
            return self.name_nl or self.name_en
        return self.name_en or self.name_nl

    def __str__(self) -> str:
        return self.display_name


class Company(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="companies",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    location = models.CharField(max_length=180, blank=True)
    logo_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


CURRENCY_SYMBOLS = {
    "EUR": "€",
    "USD": "$",
    "INR": "₹",
    "GBP": "£",
}


class Job(models.Model):
    class JobTypeLegacy(models.TextChoices):
        FULL_TIME = "full_time", "Full Time"
        PART_TIME = "part_time", "Part Time"
        CONTRACT = "contract", "Contract"
        TEMPORARY = "temporary", "Temporary"
        INTERNSHIP = "internship", "Internship"

    class ExperienceLevelLegacy(models.TextChoices):
        ENTRY = "entry", "Entry"
        MID = "mid", "Mid"
        SENIOR = "senior", "Senior"

    class Currency(models.TextChoices):
        EUR = "EUR", "Euro (€)"
        USD = "USD", "US Dollar ($)"
        INR = "INR", "Indian Rupee (₹)"
        GBP = "GBP", "British Pound (£)"

    # Legacy single-language fields (kept)
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="jobs")
    category = models.ForeignKey(
        JobCategory, on_delete=models.SET_NULL, related_name="jobs", null=True, blank=True
    )
    location = models.CharField(max_length=180)
    job_type_ref = models.ForeignKey(JobType, on_delete=models.SET_NULL, related_name="jobs", null=True, blank=True)
    experience_level_ref = models.ForeignKey(
        ExperienceLevel, on_delete=models.SET_NULL, related_name="jobs", null=True, blank=True
    )
    job_type = models.CharField(
        max_length=20, choices=JobTypeLegacy.choices, default=JobTypeLegacy.FULL_TIME
    )
    experience_level = models.CharField(
        max_length=20, choices=ExperienceLevelLegacy.choices, default=ExperienceLevelLegacy.ENTRY
    )
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=8, default=Currency.EUR, choices=Currency.choices)
    description = models.TextField()
    requirements = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    benefits = models.TextField(blank=True, default="")

    # Multilingual fields (preferred)
    title_en = models.CharField(max_length=200, blank=True, default="")
    title_nl = models.CharField(max_length=200, blank=True, default="")
    description_en = models.TextField(blank=True, default="")
    description_nl = models.TextField(blank=True, default="")
    requirements_en = models.TextField(blank=True, default="")
    requirements_nl = models.TextField(blank=True, default="")
    responsibilities_en = models.TextField(blank=True, default="")
    responsibilities_nl = models.TextField(blank=True, default="")
    benefits_en = models.TextField(blank=True, default="")
    benefits_nl = models.TextField(blank=True, default="")
    deadline = models.DateField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    image = models.ImageField(upload_to="jobs/", null=True, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def image_url(self) -> str:
        try:
            if self.image and getattr(self.image, "url", ""):
                return self.image.url
        except Exception:
            pass
        return ""

    class Meta:
        ordering = ["-posted_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = _generate_unique_slug_for_instance(
                instance=self,
                base=(self.title_en or self.title_nl or self.title or "job"),
                slug_field_name="slug",
            )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title_i18n or self.title

    @property
    def title_i18n(self) -> str:
        lang = (get_language() or "en").split("-")[0]
        if lang == "nl":
            return self.title_nl or self.title_en or self.title
        return self.title_en or self.title_nl or self.title

    @property
    def description_i18n(self) -> str:
        lang = (get_language() or "en").split("-")[0]
        if lang == "nl":
            return self.description_nl or self.description_en or self.description
        return self.description_en or self.description_nl or self.description

    @property
    def requirements_i18n(self) -> str:
        lang = (get_language() or "en").split("-")[0]
        if lang == "nl":
            return self.requirements_nl or self.requirements_en or self.requirements
        return self.requirements_en or self.requirements_nl or self.requirements

    @property
    def responsibilities_i18n(self) -> str:
        lang = (get_language() or "en").split("-")[0]
        if lang == "nl":
            return self.responsibilities_nl or self.responsibilities_en or self.responsibilities
        return self.responsibilities_en or self.responsibilities_nl or self.responsibilities

    @property
    def benefits_i18n(self) -> str:
        lang = (get_language() or "en").split("-")[0]
        if lang == "nl":
            return self.benefits_nl or self.benefits_en or self.benefits
        return self.benefits_en or self.benefits_nl or self.benefits

    @property
    def currency_symbol(self) -> str:
        return CURRENCY_SYMBOLS.get((self.currency or "").upper(), self.currency or "")

    @property
    def job_type_label(self) -> str:
        if self.job_type_ref_id:
            return self.job_type_ref.display_name
        return self.job_type or ""

    @property
    def experience_level_label(self) -> str:
        if self.experience_level_ref_id:
            return self.experience_level_ref.display_name
        return self.experience_level or ""
