from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from .web_views import (
    dashboard_home,
    frontend_page,
    health_check,
)

urlpatterns = [
    path("accounts/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("accounts/logout/", auth_views.LogoutView.as_view(next_page="/accounts/login/"), name="logout"),
    path("dashboard/", dashboard_home, name="dashboard-home"),
    path("adminpanel/", include("apps.adminpanel.urls")),
    path("", include("apps.applications.web_urls")),
    path("jobs/", include("apps.jobs.web_urls")),
    path("health/", health_check, name="health-check"),
    path("api/", include("apps.api.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path("api/docs/swagger/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs-swagger"),
    path("api/docs/redoc/", SpectacularRedocView.as_view(url_name="api-schema"), name="api-docs-redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path("", frontend_page, name="frontend-index"),
    path("<path:page_path>", frontend_page, name="frontend-page"),
]
