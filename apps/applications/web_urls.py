from django.urls import path

from . import web_views

urlpatterns = [
    path("account/", web_views.user_account, name="user-account"),
    # Legacy redirects so old bookmarks / code still work
    path("dashboard/user/", web_views.user_dashboard, name="user-dashboard"),
    path("dashboard/user/applications/", web_views.user_applications, name="user-applications"),
]
