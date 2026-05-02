from rest_framework import permissions, viewsets

from apps.accounts.permissions import IsAdminOrReadOnly, is_admin_user

from .models import BlogCategory, BlogPost, Partner, Service, Testimonial
from .serializers import (
    BlogCategorySerializer,
    BlogPostSerializer,
    PartnerSerializer,
    ServiceSerializer,
    TestimonialSerializer,
)


class TestimonialPermission(permissions.BasePermission):
    """Public read; any authenticated user can submit; only admin updates/deletes."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == "POST":
            return bool(request.user and request.user.is_authenticated)
        return is_admin_user(request.user)


class BlogCategoryViewSet(viewsets.ModelViewSet):
    queryset = BlogCategory.objects.all()
    serializer_class = BlogCategorySerializer
    permission_classes = [IsAdminOrReadOnly]


class BlogPostViewSet(viewsets.ModelViewSet):
    queryset = BlogPost.objects.select_related("category").all()
    serializer_class = BlogPostSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category_id=category)

        is_published = self.request.query_params.get("is_published")
        if is_published is not None:
            queryset = queryset.filter(is_published=is_published.lower() in {"1", "true", "yes"})

        search = self.request.query_params.get("search")
        if search:
            queryset = queryset.filter(title__icontains=search)

        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            queryset = queryset.filter(is_published=True)
        return queryset

    permission_classes = [IsAdminOrReadOnly]


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)
        return queryset


class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    permission_classes = [TestimonialPermission]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        if not is_admin_user(self.request.user):
            queryset = queryset.filter(is_active=True)
        return queryset

    def perform_create(self, serializer):
        # User-submitted reviews start as inactive (pending admin approval).
        # Admins can override `is_active` by passing it in the payload.
        user = self.request.user
        is_active = False
        if is_admin_user(user) and "is_active" in serializer.validated_data:
            is_active = bool(serializer.validated_data.get("is_active"))

        author_name = serializer.validated_data.get("author_name") or ""
        if not author_name and user.is_authenticated:
            author_name = (
                f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
                or getattr(user, "email", "User")
            )

        serializer.save(is_active=is_active, author_name=author_name)


class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        if not (self.request.user.is_authenticated and self.request.user.is_staff):
            queryset = queryset.filter(is_active=True)
        return queryset
