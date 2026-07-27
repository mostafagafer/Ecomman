from django.contrib import admin
from .models import EmailVerificationOTP, LoginLockout

# Register your models here.


@admin.register(EmailVerificationOTP)
class EmailVerificationOTPAdmin(admin.ModelAdmin):
    list_display = ("email", "user", "expires_at", "used_at", "attempts", "created_at")
    search_fields = ("email", "user__email", "user__username")
    list_filter = ("used_at", "expires_at")
    readonly_fields = ("code_hash", "created_at")


@admin.register(LoginLockout)
class LoginLockoutAdmin(admin.ModelAdmin):
    list_display = ("email", "ip_address", "failed_attempts", "locked_until", "last_failed_at")
    search_fields = ("email", "ip_address")
    list_filter = ("locked_until",)

