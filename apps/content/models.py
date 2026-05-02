from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.utils.translation import get_language


def _current_lang() -> str:
    return (get_language() or "en").split("-")[0]


class BlogCategory(models.Model):
    name = models.CharField(max_length=120, unique=True)
    name_en = models.CharField(max_length=120, blank=True, default="")
    name_nl = models.CharField(max_length=120, blank=True, default="")
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Blog categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name_nl or self.name)
        super().save(*args, **kwargs)

    @property
    def display_name(self) -> str:
        if _current_lang() == "nl":
            return self.name_nl or self.name_en or self.name
        return self.name_en or self.name_nl or self.name

    def __str__(self) -> str:
        return self.display_name


class BlogPost(models.Model):
    title = models.CharField(max_length=220)
    slug = models.SlugField(max_length=240, unique=True, blank=True)
    excerpt = models.TextField(blank=True)
    content = models.TextField()

    title_en = models.CharField(max_length=220, blank=True, default="")
    title_nl = models.CharField(max_length=220, blank=True, default="")
    excerpt_en = models.TextField(blank=True, default="")
    excerpt_nl = models.TextField(blank=True, default="")
    content_en = models.TextField(blank=True, default="")
    content_nl = models.TextField(blank=True, default="")

    author_name = models.CharField(max_length=120, default="Inter Labour Team")
    featured_image = models.ImageField(upload_to="blog/", null=True, blank=True)
    featured_image_url = models.URLField(blank=True)
    category = models.ForeignKey(
        BlogCategory, on_delete=models.SET_NULL, related_name="posts", null=True, blank=True
    )
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title_en or self.title_nl or self.title)
        super().save(*args, **kwargs)

    @property
    def title_i18n(self) -> str:
        if _current_lang() == "nl":
            return self.title_nl or self.title_en or self.title
        return self.title_en or self.title_nl or self.title

    @property
    def excerpt_i18n(self) -> str:
        if _current_lang() == "nl":
            return self.excerpt_nl or self.excerpt_en or self.excerpt
        return self.excerpt_en or self.excerpt_nl or self.excerpt

    @property
    def content_i18n(self) -> str:
        if _current_lang() == "nl":
            return self.content_nl or self.content_en or self.content
        return self.content_en or self.content_nl or self.content

    @property
    def image_url(self) -> str:
        try:
            if self.featured_image and getattr(self.featured_image, "url", ""):
                return self.featured_image.url
        except Exception:
            pass
        return self.featured_image_url or ""

    def __str__(self) -> str:
        return self.title_i18n or self.title


class Service(models.Model):
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    short_description = models.CharField(max_length=300, blank=True)
    details = models.TextField(blank=True)

    name_en = models.CharField(max_length=180, blank=True, default="")
    name_nl = models.CharField(max_length=180, blank=True, default="")
    short_description_en = models.CharField(max_length=300, blank=True, default="")
    short_description_nl = models.CharField(max_length=300, blank=True, default="")
    details_en = models.TextField(blank=True, default="")
    details_nl = models.TextField(blank=True, default="")

    icon_name = models.CharField(max_length=80, blank=True)
    image = models.ImageField(upload_to="services/", null=True, blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en or self.name_nl or self.name)
        super().save(*args, **kwargs)

    @property
    def name_i18n(self) -> str:
        if _current_lang() == "nl":
            return self.name_nl or self.name_en or self.name
        return self.name_en or self.name_nl or self.name

    @property
    def short_description_i18n(self) -> str:
        if _current_lang() == "nl":
            return self.short_description_nl or self.short_description_en or self.short_description
        return self.short_description_en or self.short_description_nl or self.short_description

    @property
    def details_i18n(self) -> str:
        if _current_lang() == "nl":
            return self.details_nl or self.details_en or self.details
        return self.details_en or self.details_nl or self.details

    @property
    def image_url(self) -> str:
        try:
            if self.image and getattr(self.image, "url", ""):
                return self.image.url
        except Exception:
            pass
        return ""

    def __str__(self) -> str:
        return self.name_i18n or self.name


class Testimonial(models.Model):
    """A client testimonial shown in the 'What Our Clients Say' section."""

    author_name = models.CharField(max_length=180)
    author_role = models.CharField(max_length=180, blank=True, help_text="e.g. Operations Manager, Acme Corp")
    author_role_en = models.CharField(max_length=180, blank=True, default="")
    author_role_nl = models.CharField(max_length=180, blank=True, default="")

    message_en = models.TextField(blank=True, default="")
    message_nl = models.TextField(blank=True, default="")
    message = models.TextField(blank=True, default="", help_text="Legacy single-language fallback")

    photo = models.ImageField(upload_to="testimonials/", null=True, blank=True)
    rating = models.PositiveSmallIntegerField(default=5, help_text="1–5 stars")
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.message:
            self.message = self.message_en or self.message_nl or ""
        super().save(*args, **kwargs)

    @property
    def author_role_i18n(self) -> str:
        if _current_lang() == "nl":
            return self.author_role_nl or self.author_role_en or self.author_role
        return self.author_role_en or self.author_role_nl or self.author_role

    @property
    def message_i18n(self) -> str:
        if _current_lang() == "nl":
            return self.message_nl or self.message_en or self.message
        return self.message_en or self.message_nl or self.message

    @property
    def photo_url(self) -> str:
        try:
            if self.photo and getattr(self.photo, "url", ""):
                return self.photo.url
        except Exception:
            pass
        return ""

    def __str__(self) -> str:
        return self.author_name


class Partner(models.Model):
    """A partner / client logo shown in the homepage logo strip."""

    name = models.CharField(max_length=180)
    logo = models.ImageField(upload_to="partners/", null=True, blank=True)
    logo_url = models.URLField(blank=True, help_text="Optional URL to a logo image hosted elsewhere")
    website = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]

    @property
    def logo_image_url(self) -> str:
        try:
            if self.logo and getattr(self.logo, "url", ""):
                return self.logo.url
        except Exception:
            pass
        return self.logo_url or ""

    def __str__(self) -> str:
        return self.name
