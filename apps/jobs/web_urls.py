from django.urls import path

from . import web_views

urlpatterns = [
    path("", web_views.job_list, name="jobs-list"),
    path("<slug:slug>/", web_views.job_detail, name="jobs-detail"),
    path("<slug:slug>/apply/", web_views.job_apply, name="jobs-apply"),
]

