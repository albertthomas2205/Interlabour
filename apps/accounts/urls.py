from django.urls import path

from .views import (
    ForgotPasswordAPIView,
    LoginAPIView,
    LogoutAPIView,
    MeAPIView,
    RefreshAPIView,
    RegisterAPIView,
    ResendEmailOTPAPIView,
    ResetPasswordAPIView,
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
    path("forgot-password/", ForgotPasswordAPIView.as_view(), name="auth-forgot-password"),
    path("reset-password/", ResetPasswordAPIView.as_view(), name="auth-reset-password"),
]
