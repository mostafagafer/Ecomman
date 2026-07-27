from django.conf import settings
from django.db import models


class EmailVerificationOTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="email_otps")
    email = models.EmailField()
    code_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(blank=True, null=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["email", "expires_at"]),
            models.Index(fields=["user", "used_at"]),
        ]

    def __str__(self):
        return f"OTP for {self.email}"


class LoginLockout(models.Model):
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    failed_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(blank=True, null=True)
    last_user_agent = models.CharField(max_length=255, blank=True, default="")
    last_failed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("email", "ip_address")
        indexes = [
            models.Index(fields=["email", "ip_address"]),
            models.Index(fields=["locked_until"]),
        ]

    def __str__(self):
        return f"{self.email} @ {self.ip_address}"
