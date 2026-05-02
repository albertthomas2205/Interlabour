from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.communication.views import ContactMessageViewSet
from apps.content.views import (
    BlogCategoryViewSet,
    BlogPostViewSet,
    PartnerViewSet,
    ServiceViewSet,
    TestimonialViewSet,
)
from apps.jobs.views import ApplicationViewSet, CompanyViewSet, JobCategoryViewSet, JobViewSet
from apps.people.views import CandidateProfileViewSet

router = DefaultRouter()
router.register(r"job-categories", JobCategoryViewSet, basename="job-category")
router.register(r"companies", CompanyViewSet, basename="company")
router.register(r"jobs", JobViewSet, basename="job")
router.register(r"applications", ApplicationViewSet, basename="application")
router.register(r"candidates", CandidateProfileViewSet, basename="candidate")
router.register(r"blog-categories", BlogCategoryViewSet, basename="blog-category")
router.register(r"blog-posts", BlogPostViewSet, basename="blog-post")
router.register(r"services", ServiceViewSet, basename="service")
router.register(r"testimonials", TestimonialViewSet, basename="testimonial")
router.register(r"partners", PartnerViewSet, basename="partner")
router.register(r"contact-messages", ContactMessageViewSet, basename="contact-message")

urlpatterns = [
    path("auth/", include("apps.accounts.urls")),
    path("", include(router.urls)),
]
