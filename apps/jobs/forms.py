from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.applications.models import Application
from .models import Company, Job


ALLOWED_DOC_EXTENSIONS = {".pdf", ".jpg", ".jpeg", ".png"}
ALLOWED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}
MAX_DOC_SIZE_MB = 5
MAX_DOC_SIZE_BYTES = MAX_DOC_SIZE_MB * 1024 * 1024


def _validate_uploaded_file(file_obj, allowed_extensions, label):
    if file_obj is None:
        return
    name = (getattr(file_obj, "name", "") or "").lower()
    ext = name[name.rfind(".") :] if "." in name else ""
    if ext not in allowed_extensions:
        raise ValidationError(
            _("%(label)s must be one of: %(exts)s")
            % {"label": label, "exts": ", ".join(sorted(allowed_extensions))}
        )
    size = getattr(file_obj, "size", 0)
    if size and size > MAX_DOC_SIZE_BYTES:
        raise ValidationError(
            _("%(label)s exceeds maximum size of %(max)d MB.")
            % {"label": label, "max": MAX_DOC_SIZE_MB}
        )


class CompanyProfileForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ["name", "description", "website", "email", "phone", "location", "logo_url", "is_active"]


class CompanyJobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            "title",
            "category",
            "location",
            "job_type",
            "experience_level",
            "salary_min",
            "salary_max",
            "currency",
            "description",
            "requirements",
            "responsibilities",
            "deadline",
            "is_featured",
            "is_active",
        ]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }


class JobApplicationForm(forms.ModelForm):
    full_name = forms.CharField(
        label=_("Full name"),
        max_length=180,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": _("Your full name")}),
    )
    email = forms.EmailField(
        label=_("Email address"),
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": _("you@example.com")}),
    )
    phone = forms.CharField(
        label=_("Phone number"),
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": _("+91 9876543210")}),
    )
    resume = forms.FileField(
        label=_("Resume / CV"),
        required=True,
        widget=forms.FileInput(attrs={"accept": ".pdf,.doc,.docx"}),
        help_text=_("Allowed: PDF, DOC, DOCX. Max 5 MB."),
    )
    aadhaar_card = forms.FileField(
        label=_("Aadhaar Card"),
        required=True,
        widget=forms.FileInput(attrs={"accept": ".pdf,.jpg,.jpeg,.png"}),
        help_text=_("Allowed: PDF, JPG, JPEG, PNG. Max 5 MB."),
    )
    pan_card = forms.FileField(
        label=_("PAN Card"),
        required=True,
        widget=forms.FileInput(attrs={"accept": ".pdf,.jpg,.jpeg,.png"}),
        help_text=_("Allowed: PDF, JPG, JPEG, PNG. Max 5 MB."),
    )
    passport = forms.FileField(
        label=_("Passport"),
        required=True,
        widget=forms.FileInput(attrs={"accept": ".pdf,.jpg,.jpeg,.png"}),
        help_text=_("Allowed: PDF, JPG, JPEG, PNG. Max 5 MB."),
    )
    cover_letter = forms.CharField(
        label=_("Cover letter (optional)"),
        required=False,
        widget=forms.Textarea(attrs={"rows": 5, "placeholder": _("Tell us why you are a great fit…")}),
    )

    class Meta:
        model = Application
        fields = [
            "full_name",
            "email",
            "phone",
            "resume",
            "aadhaar_card",
            "pan_card",
            "passport",
            "cover_letter",
        ]

    def clean_resume(self):
        f = self.cleaned_data.get("resume")
        _validate_uploaded_file(f, ALLOWED_RESUME_EXTENSIONS, _("Resume"))
        return f

    def clean_aadhaar_card(self):
        f = self.cleaned_data.get("aadhaar_card")
        _validate_uploaded_file(f, ALLOWED_DOC_EXTENSIONS, _("Aadhaar Card"))
        return f

    def clean_pan_card(self):
        f = self.cleaned_data.get("pan_card")
        _validate_uploaded_file(f, ALLOWED_DOC_EXTENSIONS, _("PAN Card"))
        return f

    def clean_passport(self):
        f = self.cleaned_data.get("passport")
        _validate_uploaded_file(f, ALLOWED_DOC_EXTENSIONS, _("Passport"))
        return f
