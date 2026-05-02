from rest_framework import serializers

from apps.applications.models import Application
from .models import Company, Job, JobCategory


class JobCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobCategory
        fields = "__all__"


class CompanySerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source="owner.email", read_only=True)

    class Meta:
        model = Company
        fields = "__all__"


class JobSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name", read_only=True)
    category_name = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    requirements = serializers.SerializerMethodField()
    responsibilities = serializers.SerializerMethodField()
    benefits = serializers.SerializerMethodField()
    job_type_label = serializers.SerializerMethodField()
    experience_level_label = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    currency_symbol = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = (
            "id",
            "slug",
            "company",
            "company_name",
            "category",
            "category_name",
            "location",
            "job_type",
            "job_type_ref",
            "job_type_label",
            "experience_level",
            "experience_level_ref",
            "experience_level_label",
            "salary_min",
            "salary_max",
            "currency",
            "currency_symbol",
            "deadline",
            "is_featured",
            "is_active",
            "posted_at",
            "updated_at",
            "title",
            "description",
            "requirements",
            "responsibilities",
            "benefits",
            "image_url",
        )

    def get_category_name(self, obj):
        if not obj.category:
            return ""
        return obj.category.display_name

    def get_title(self, obj):
        return obj.title_i18n

    def get_description(self, obj):
        return obj.description_i18n

    def get_requirements(self, obj):
        return obj.requirements_i18n

    def get_responsibilities(self, obj):
        return obj.responsibilities_i18n

    def get_benefits(self, obj):
        return obj.benefits_i18n

    def get_currency_symbol(self, obj):
        return obj.currency_symbol

    def get_job_type_label(self, obj):
        return obj.job_type_label

    def get_experience_level_label(self, obj):
        return obj.experience_level_label

    def get_image_url(self, obj):
        url = obj.image_url
        if not url:
            return ""
        request = self.context.get("request")
        if request is not None:
            return request.build_absolute_uri(url)
        return url


class ApplicationSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    applicant_email = serializers.EmailField(source="applicant.email", read_only=True)
    resume_url = serializers.SerializerMethodField()
    aadhaar_card_url = serializers.SerializerMethodField()
    pan_card_url = serializers.SerializerMethodField()
    passport_url = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = "__all__"
        read_only_fields = ("applicant",)
        extra_kwargs = {
            "full_name": {"required": False},
            "email": {"required": False},
            "resume": {"required": True, "allow_null": False},
        }

    def _abs_url(self, field):
        if not field:
            return None
        request = self.context.get("request")
        url = field.url
        return request.build_absolute_uri(url) if request else url

    def get_resume_url(self, obj):
        return self._abs_url(obj.resume)

    def get_aadhaar_card_url(self, obj):
        return self._abs_url(obj.aadhaar_card)

    def get_pan_card_url(self, obj):
        return self._abs_url(obj.pan_card)

    def get_passport_url(self, obj):
        return self._abs_url(obj.passport)
