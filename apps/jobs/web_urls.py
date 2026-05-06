from django.urls import path

from . import web_views

urlpatterns = [
    path("", web_views.job_list, name="jobs-list"),
    path("alerts/subscribe/", web_views.job_alert_subscribe, name="jobs-alert-subscribe"),
    path("alerts/confirmed/", web_views.job_alert_confirmed, name="jobs-alert-confirmed"),
    path("<slug:slug>/", web_views.job_detail, name="jobs-detail"),
    path("<slug:slug>/apply/", web_views.job_apply, name="jobs-apply"),
]

