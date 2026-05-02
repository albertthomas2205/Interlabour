from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.admin_login, name="adminpanel-login"),
    path("logout/", views.admin_logout, name="adminpanel-logout"),
    path("", views.dashboard, name="adminpanel-dashboard"),

    path("jobs/", views.job_list, name="adminpanel-jobs"),
    path("jobs/new/", views.job_create, name="adminpanel-job-create"),
    path("jobs/<int:job_id>/edit/", views.job_edit, name="adminpanel-job-edit"),
    path("jobs/<int:job_id>/delete/", views.job_delete, name="adminpanel-job-delete"),

    path("categories/", views.category_list, name="adminpanel-categories"),
    path("categories/new/", views.category_create, name="adminpanel-category-create"),
    path("categories/<int:category_id>/edit/", views.category_edit, name="adminpanel-category-edit"),
    path("categories/<int:category_id>/delete/", views.category_delete, name="adminpanel-category-delete"),

    path("job-types/", views.job_type_list, name="adminpanel-job-types"),
    path("job-types/new/", views.job_type_create, name="adminpanel-job-type-create"),
    path("job-types/<int:item_id>/edit/", views.job_type_edit, name="adminpanel-job-type-edit"),
    path("job-types/<int:item_id>/delete/", views.job_type_delete, name="adminpanel-job-type-delete"),

    path("experience-levels/", views.experience_level_list, name="adminpanel-experience-levels"),
    path("experience-levels/new/", views.experience_level_create, name="adminpanel-experience-level-create"),
    path("experience-levels/<int:item_id>/edit/", views.experience_level_edit, name="adminpanel-experience-level-edit"),
    path("experience-levels/<int:item_id>/delete/", views.experience_level_delete, name="adminpanel-experience-level-delete"),

    path("applications/", views.application_list, name="adminpanel-applications"),
    path(
        "applications/<int:app_id>/documents/download-all/",
        views.application_download_all_documents,
        name="adminpanel-application-download-all",
    ),
    path(
        "applications/<int:app_id>/documents/<str:kind>/view/",
        views.application_serve_document,
        {"as_attachment": False},
        name="adminpanel-application-document-view",
    ),
    path(
        "applications/<int:app_id>/documents/<str:kind>/download/",
        views.application_serve_document,
        {"as_attachment": True},
        name="adminpanel-application-document-download",
    ),
    path("applications/<int:app_id>/status/", views.application_update_status, name="adminpanel-application-status"),

    path("services/", views.service_list, name="adminpanel-services"),
    path("services/new/", views.service_create, name="adminpanel-service-create"),
    path("services/<int:item_id>/edit/", views.service_edit, name="adminpanel-service-edit"),
    path("services/<int:item_id>/delete/", views.service_delete, name="adminpanel-service-delete"),

    path("blog-posts/", views.blog_post_list, name="adminpanel-blog-posts"),
    path("blog-posts/new/", views.blog_post_create, name="adminpanel-blog-post-create"),
    path("blog-posts/<int:item_id>/edit/", views.blog_post_edit, name="adminpanel-blog-post-edit"),
    path("blog-posts/<int:item_id>/delete/", views.blog_post_delete, name="adminpanel-blog-post-delete"),

    path("blog-categories/", views.blog_category_list, name="adminpanel-blog-categories"),
    path("blog-categories/new/", views.blog_category_create, name="adminpanel-blog-category-create"),
    path("blog-categories/<int:item_id>/edit/", views.blog_category_edit, name="adminpanel-blog-category-edit"),
    path("blog-categories/<int:item_id>/delete/", views.blog_category_delete, name="adminpanel-blog-category-delete"),

    path("testimonials/", views.testimonial_list, name="adminpanel-testimonials"),
    path("testimonials/new/", views.testimonial_create, name="adminpanel-testimonial-create"),
    path("testimonials/<int:item_id>/edit/", views.testimonial_edit, name="adminpanel-testimonial-edit"),
    path("testimonials/<int:item_id>/approve/", views.testimonial_approve, name="adminpanel-testimonial-approve"),
    path("testimonials/<int:item_id>/delete/", views.testimonial_delete, name="adminpanel-testimonial-delete"),

    path("partners/", views.partner_list, name="adminpanel-partners"),
    path("partners/new/", views.partner_create, name="adminpanel-partner-create"),
    path("partners/<int:item_id>/edit/", views.partner_edit, name="adminpanel-partner-edit"),
    path("partners/<int:item_id>/delete/", views.partner_delete, name="adminpanel-partner-delete"),
]
