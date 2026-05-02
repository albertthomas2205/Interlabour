from django.urls import path

from .views import (
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    RefreshAPIView,
    RegisterAPIView,
    ResendEmailOTPAPIView,
    VerifyEmailOTPAPIView,
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="auth-register"),
    path("verify-email-otp/", VerifyEmailOTPAPIView.as_view(), name="auth-verify-email-otp"),
    path("resend-email-otp/", ResendEmailOTPAPIView.as_view(), name="auth-resend-email-otp"),
    path("login/", LoginAPIView.as_view(), name="auth-login"),
    path("refresh/", RefreshAPIView.as_view(), name="auth-refresh"),
    path("logout/", LogoutAPIView.as_view(), name="auth-logout"),
    path("me/", MeAPIView.as_view(), name="auth-me"),
]
