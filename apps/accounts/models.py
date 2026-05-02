import secrets
from datetime import timedelta
from hashlib import sha256

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractUser):
    class UserType(models.TextChoices):
        ADMIN = "admin", "Admin"
        COMPANY = "company", "Company"
        NORMAL = "normal", "User"

    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=20, choices=UserType.choices, default=UserType.NORMAL)
    email_verified = models.BooleanField(default=False)
    cv = models.FileField(upload_to="cvs/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self) -> str:
        return self.email


class EmailOTP(models.Model):
    class Purpose(models.TextChoices):
        REGISTRATION = "registration", "Registration"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_otps")
    email = models.EmailField()
    code_hash = models.CharField(max_length=64)
    purpose = models.CharField(max_length=30, choices=Purpose.choices, default=Purpose.REGISTRATION)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @staticmethod
    def generate_code(length: int = 6) -> str:
        digits = "0123456789"
        return "".join(secrets.choice(digits) for _ in range(length))

    @staticmethod
    def hash_code(code: str) -> str:
        return sha256(code.encode("utf-8")).hexdigest()

    @classmethod
    def create_for_user(cls, user, purpose=Purpose.REGISTRATION):
        code = cls.generate_code()
        expiry_minutes = int(getattr(settings, "OTP_EXPIRY_MINUTES", 10))
        record = cls.objects.create(
            user=user,
            email=user.email,
            code_hash=cls.hash_code(code),
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=expiry_minutes),
        )
        return record, code

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    def verify_code(self, code: str) -> bool:
        return self.code_hash == self.hash_code(code)


class PendingRegistration(models.Model):
    email = models.EmailField(db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    password_hash = models.CharField(max_length=128)
    user_type = models.CharField(max_length=20, choices=User.UserType.choices, default=User.UserType.NORMAL)
    otp_code_hash = models.CharField(max_length=64)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @classmethod
    def create_pending(
        cls,
        *,
        email: str,
        first_name: str,
        last_name: str,
        password_hash: str,
        user_type: str,
    ):
        code = EmailOTP.generate_code()
        expiry_minutes = int(getattr(settings, "OTP_EXPIRY_MINUTES", 10))
        record = cls.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=password_hash,
            user_type=user_type,
            otp_code_hash=EmailOTP.hash_code(code),
            expires_at=timezone.now() + timedelta(minutes=expiry_minutes),
        )
        return record, code

    def refresh_otp(self):
        code = EmailOTP.generate_code()
        expiry_minutes = int(getattr(settings, "OTP_EXPIRY_MINUTES", 10))
        self.otp_code_hash = EmailOTP.hash_code(code)
        self.expires_at = timezone.now() + timedelta(minutes=expiry_minutes)
        self.attempts = 0
        self.is_used = False
        self.save(update_fields=["otp_code_hash", "expires_at", "attempts", "is_used"])
        return code

    def is_expired(self) -> bool:
        return timezone.now() >= self.expires_at

    def verify_code(self, code: str) -> bool:
        return self.otp_code_hash == EmailOTP.hash_code(code)
