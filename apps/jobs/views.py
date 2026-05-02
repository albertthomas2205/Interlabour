from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.permissions import (
    IsAdminOrCompanyType,
    IsAdminOrReadOnly,
    is_admin_user,
    is_company_user,
    is_normal_user,
)

from apps.applications.models import Application
from .models import Company, Job, JobCategory
from .serializers import ApplicationSerializer, CompanySerializer, JobCategorySerializer, JobSerializer


class JobCategoryViewSet(viewsets.ModelViewSet):
    queryset = JobCategory.objects.all()
    serializer_class = JobCategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdminOrCompanyType]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        user = self.request.user
        if is_admin_user(user):
            serializer.save()
            return
        if Company.objects.filter(owner=user).exists():
            raise ValidationError({"detail": "You already have a company profile."})
        serializer.save(owner=user)

    def perform_update(self, serializer):
        company = self.get_object()
        user = self.request.user
        if not is_admin_user(user) and company.owner_id != user.id:
            raise PermissionDenied("You can only edit your own company profile.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not is_admin_user(user) and instance.owner_id != user.id:
            raise PermissionDenied("You can only delete your own company profile.")
        instance.delete()


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.select_related("company", "category").all()
    serializer_class = JobSerializer

    def get_permissions(self):
        if self.action in {"list", "retrieve"}:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [IsAdminOrCompanyType]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        params = self.request.query_params
        user = self.request.user

        mine = params.get("mine")
        if mine and mine.lower() in {"1", "true", "yes"} and user.is_authenticated and is_company_user(user):
            queryset = queryset.filter(company__owner=user)

        is_active = params.get("is_active")
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() in {"1", "true", "yes"})
        elif not (user.is_authenticated and (is_admin_user(user) or is_company_user(user))):
            queryset = queryset.filter(is_active=True)

        company_id = params.get("company")
        if company_id:
            queryset = queryset.filter(company_id=company_id)

        category_id = params.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        job_type = params.get("job_type")
        if job_type:
            queryset = queryset.filter(job_type=job_type)

        location = params.get("location")
        if location:
            queryset = queryset.filter(location__icontains=location)

        is_featured = params.get("is_featured")
        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured.lower() in {"1", "true", "yes"})

        search = params.get("search")
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(description__icontains=search)
                | Q(company__name__icontains=search)
                | Q(location__icontains=search)
            )

        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        if is_admin_user(user):
            serializer.save()
            return

        company = serializer.validated_data.get("company")
        if company is None:
            company = Company.objects.filter(owner=user).first()
            if company is None:
                raise ValidationError({"company": "Create your company profile first."})
            serializer.save(company=company)
            return

        if company.owner_id != user.id:
            raise PermissionDenied("You can only post jobs for your own company.")
        serializer.save()

    def perform_update(self, serializer):
        job = self.get_object()
        user = self.request.user
        if not is_admin_user(user) and job.company.owner_id != user.id:
            raise PermissionDenied("You can only edit jobs for your own company.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not is_admin_user(user) and instance.company.owner_id != user.id:
            raise PermissionDenied("You can only delete jobs for your own company.")
        instance.delete()


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = Application.objects.select_related("job").all()
    serializer_class = ApplicationSerializer

    def get_permissions(self):
        permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if is_admin_user(user):
            return queryset
        if is_company_user(user):
            return queryset.filter(job__company__owner=user)
        return queryset.filter(applicant=user)

    def perform_create(self, serializer):
        user = self.request.user
        if not is_normal_user(user):
            raise PermissionDenied("Only user accounts can apply for jobs.")

        full_name = serializer.validated_data.get("full_name") or f"{user.first_name} {user.last_name}".strip()
        if not full_name:
            full_name = user.email

        email = serializer.validated_data.get("email") or user.email
        serializer.save(applicant=user, full_name=full_name, email=email)

    def perform_update(self, serializer):
        application = self.get_object()
        user = self.request.user
        if is_admin_user(user):
            serializer.save()
            return

        if is_company_user(user) and application.job.company.owner_id == user.id:
            if set(serializer.validated_data.keys()) - {"status"}:
                raise ValidationError({"detail": "Company can only update application status."})
            serializer.save()
            return

        raise PermissionDenied("You are not allowed to update this application.")

    def perform_destroy(self, instance):
        user = self.request.user
        if is_admin_user(user):
            instance.delete()
            return
        if is_normal_user(user) and instance.applicant_id == user.id:
            instance.delete()
            return
        raise PermissionDenied("You are not allowed to delete this application.")
