import os

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import EmailOTP, PendingRegistration
from .services import send_pending_registration_otp, send_registration_otp

User = get_user_model()


def _request_language(serializer_self) -> str | None:
    request = serializer_self.context.get("request")
    return getattr(request, "LANGUAGE_CODE", None) if request else None


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8)
    first_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    last_name = serializers.CharField(required=False, allow_blank=True, max_length=150)
    # Only applicant users can self-register.

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()

    def create(self, validated_data):
        user_type = User.UserType.NORMAL
        email = validated_data["email"]
        PendingRegistration.objects.filter(email__iexact=email, is_used=False).update(is_used=True)
        pending, otp_code = PendingRegistration.create_pending(
            email=email,
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            password_hash=make_password(validated_data["password"]),
            user_type=user_type,
        )

        try:
            send_pending_registration_otp(pending, otp_code, language_code=_request_language(self))
        except Exception as exc:
            pending.delete()
            raise serializers.ValidationError({"email": f"Failed to send OTP email. {exc}"})

        return {"email": pending.email, "user_type": pending.user_type}


class VerifyEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6, min_length=6)

    def validate(self, attrs):
        email = attrs["email"].lower()
        otp = attrs["otp"].strip()
        max_attempts = int(os.getenv("OTP_MAX_ATTEMPTS", "5"))

        pending = (
            PendingRegistration.objects.filter(email__iexact=email, is_used=False)
            .order_by("-created_at")
            .first()
        )
        if pending:
            if pending.is_expired():
                raise serializers.ValidationError({"otp": "OTP expired. Please request a new OTP."})
            if pending.attempts >= max_attempts:
                raise serializers.ValidationError({"otp": "Too many attempts. Please request a new OTP."})
            if not pending.verify_code(otp):
                pending.attempts += 1
                if pending.attempts >= max_attempts:
                    pending.is_used = True
                pending.save(update_fields=["attempts", "is_used"])
                raise serializers.ValidationError({"otp": "Invalid OTP."})

            attrs["pending"] = pending
            return attrs

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "No user found with this email."})

        otp_record = (
            EmailOTP.objects.filter(
                user=user,
                email__iexact=email,
                purpose=EmailOTP.Purpose.REGISTRATION,
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )
        if not otp_record:
            raise serializers.ValidationError({"otp": "No active OTP found. Please request a new OTP."})
        if otp_record.is_expired():
            raise serializers.ValidationError({"otp": "OTP expired. Please request a new OTP."})

        if otp_record.attempts >= max_attempts:
            raise serializers.ValidationError({"otp": "Too many attempts. Please request a new OTP."})

        if not otp_record.verify_code(otp):
            otp_record.attempts += 1
            if otp_record.attempts >= max_attempts:
                otp_record.is_used = True
            otp_record.save(update_fields=["attempts", "is_used"])
            raise serializers.ValidationError({"otp": "Invalid OTP."})

        attrs["user"] = user
        attrs["otp_record"] = otp_record
        return attrs

    def save(self):
        pending = self.validated_data.get("pending")
        if pending:
            with transaction.atomic():
                if User.objects.filter(email__iexact=pending.email).exists():
                    pending.is_used = True
                    pending.save(update_fields=["is_used"])
                    raise serializers.ValidationError({"email": "An account with this email already exists."})

                username = User.objects._generate_username(pending.email)
                user = User(
                    email=pending.email,
                    username=username,
                    first_name=pending.first_name,
                    last_name=pending.last_name,
                    user_type=pending.user_type,
                    is_active=True,
                    email_verified=True,
                    is_staff=(pending.user_type == User.UserType.ADMIN),
                )
                user.password = pending.password_hash
                user.save()

                pending.is_used = True
                pending.save(update_fields=["is_used"])
            return user

        user = self.validated_data["user"]
        otp_record = self.validated_data["otp_record"]

        otp_record.is_used = True
        otp_record.save(update_fields=["is_used"])

        user.email_verified = True
        user.is_active = True
        user.save(update_fields=["email_verified", "is_active"])
        return user


class ResendEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        pending = (
            PendingRegistration.objects.filter(email__iexact=value, is_used=False)
            .order_by("-created_at")
            .first()
        )
        if pending:
            self.context["pending"] = pending
            return value.lower()

        try:
            user = User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email.")

        if user.email_verified:
            raise serializers.ValidationError("Email is already verified.")

        self.context["user"] = user
        return value.lower()

    def save(self):
        pending = self.context.get("pending")
        if pending:
            otp_code = pending.refresh_otp()
            send_pending_registration_otp(pending, otp_code, language_code=_request_language(self))
            return {"email": pending.email}

        user = self.context["user"]
        send_registration_otp(user, language_code=_request_language(self))
        return {"email": user.email}


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["email"] = user.email
        token["user_type"] = user.user_type
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        if not self.user.email_verified:
            raise AuthenticationFailed("Please verify your email with OTP before login.")
        data["user"] = {
            "id": self.user.id,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "user_type": self.user.user_type,
            "is_staff": self.user.is_staff,
            "is_superuser": self.user.is_superuser,
        }
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "user_type",
            "email_verified",
            "is_active",
        )
