import hashlib
import random

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordChangeView, PasswordResetConfirmView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from admin_soft.forms import RegistrationForm, LoginForm, UserPasswordResetForm, UserSetPasswordForm, UserPasswordChangeForm
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .auth_security import clear_login_failures, get_login_lockout, record_login_failure
from .emails import (
  send_password_changed_email,
  send_password_reset_complete_email,
  send_verification_otp_email,
  send_welcome_email,
)
from .models import EmailVerificationOTP

def landing(request):
  return render(request, 'landing/index.html')

# Authentication
class UserLoginView(LoginView):
  template_name = 'accounts/login.html'
  form_class = LoginForm

  def form_valid(self, form):
    clear_login_failures(form.cleaned_data.get("username"), self.request)
    return super().form_valid(form)

  def form_invalid(self, form):
    email = (self.request.POST.get("username") or "").strip().lower()
    if email:
      record_login_failure(email, self.request)
    return super().form_invalid(form)


def _hash_otp(code):
  return hashlib.sha256(f"{settings.SECRET_KEY}:{code}".encode("utf-8")).hexdigest()


def _create_and_send_otp(user):
  code = f"{random.SystemRandom().randint(0, 999999):06d}"
  EmailVerificationOTP.objects.filter(user=user, used_at__isnull=True).update(used_at=timezone.now())
  EmailVerificationOTP.objects.create(
    user=user,
    email=user.email,
    code_hash=_hash_otp(code),
    expires_at=timezone.now() + timezone.timedelta(minutes=settings.EMAIL_VERIFICATION_OTP_MINUTES),
  )
  send_verification_otp_email(user=user, otp_code=code)

def register(request):
  if request.user.is_authenticated:
    return redirect(settings.LOGIN_REDIRECT_URL)

  if request.method == 'POST':
    email = (request.POST.get("email") or "").strip().lower()
    existing_user = User.objects.filter(email__iexact=email).first()
    if existing_user and not existing_user.is_active:
      request.session["pending_verification_email"] = existing_user.email
      _create_and_send_otp(existing_user)
      messages.info(request, "That email is already registered but not verified. We sent a new verification code.")
      return redirect("verify_email")

    form = RegistrationForm(request.POST)
    if form.is_valid():
      user = form.save()
      _create_and_send_otp(user)
      request.session["pending_verification_email"] = user.email
      messages.success(request, "Account created. Check your email for the verification code.")
      return redirect('verify_email')
  else:
    form = RegistrationForm()

  context = { 'form': form }
  return render(request, 'accounts/register.html', context)


def verify_email(request):
  pending_email = request.session.get("pending_verification_email", "")
  if request.method == "POST":
    email = (request.POST.get("email") or pending_email).strip().lower()
    code = (request.POST.get("code") or "").strip()
    user = User.objects.filter(email__iexact=email).first()
    otp = None
    if user:
      otp = EmailVerificationOTP.objects.filter(
        user=user,
        used_at__isnull=True,
        expires_at__gt=timezone.now(),
      ).order_by("-created_at").first()
    if not user or not otp or otp.code_hash != _hash_otp(code):
      if otp:
        otp.attempts += 1
        otp.save(update_fields=["attempts"])
      messages.error(request, "Invalid or expired verification code.")
    else:
      otp.used_at = timezone.now()
      otp.save(update_fields=["used_at"])
      user.is_active = True
      user.save(update_fields=["is_active"])
      send_welcome_email(user=user)
      login(request, user, backend="admin_soft.authentication.EmailBackend")
      request.session.pop("pending_verification_email", None)
      return redirect(settings.LOGIN_REDIRECT_URL)
  return render(request, "accounts/verify_email.html", {"email": pending_email})


def resend_verification_otp(request):
  email = (request.POST.get("email") or request.session.get("pending_verification_email") or "").strip().lower()
  user = User.objects.filter(email__iexact=email, is_active=False).first()
  if user:
    _create_and_send_otp(user)
    messages.success(request, "A new verification code was sent.")
  return redirect("verify_email")

def logout_view(request):
  logout(request)
  return redirect('/accounts/login/')

class UserPasswordResetView(PasswordResetView):
  template_name = 'accounts/password_reset.html'
  form_class = UserPasswordResetForm
  email_template_name = "emails/password_reset_email.txt"
  html_email_template_name = "emails/password_reset_email.html"
  subject_template_name = "emails/password_reset_subject.txt"
  success_url = reverse_lazy("password_reset_done")
  extra_email_context = {
    "email_brand_name": settings.EMAIL_BRAND_NAME,
    "email_website_url": settings.EMAIL_WEBSITE_URL,
    "email_logo_url": settings.EMAIL_LOGO_URL,
    "email_social_linkedin_url": settings.EMAIL_SOCIAL_LINKEDIN_URL,
    "email_social_facebook_url": settings.EMAIL_SOCIAL_FACEBOOK_URL,
    "support_email": settings.SUPPORT_EMAIL,
    "frontend_base_url": settings.FRONTEND_BASE_URL,
  }

class UserPasswordResetConfirmView(PasswordResetConfirmView):
  template_name = 'accounts/password_reset_confirm.html'
  form_class = UserSetPasswordForm
  success_url = reverse_lazy("password_reset_complete")

  def form_valid(self, form):
    response = super().form_valid(form)
    send_password_reset_complete_email(user=form.user)
    return response

class UserPasswordChangeView(PasswordChangeView):
  template_name = 'accounts/password_change.html'
  form_class = UserPasswordChangeForm
  success_url = reverse_lazy("password_change_done")

  def form_valid(self, form):
    response = super().form_valid(form)
    send_password_changed_email(user=self.request.user)
    return response


def _auth_payload(user):
  refresh = RefreshToken.for_user(user)
  return {
    "user": {"id": user.id, "email": user.email, "is_email_verified": user.is_active},
    "tokens": {"access": str(refresh.access_token), "refresh": str(refresh)},
  }


class ApiRegisterView(APIView):
  permission_classes = [permissions.AllowAny]
  throttle_scope = "register"

  def post(self, request):
    form = RegistrationForm(request.data)
    if not form.is_valid():
      return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
    user = form.save()
    _create_and_send_otp(user)
    return Response({"detail": "Account created. Check your email for the verification code.", "email": user.email}, status=status.HTTP_201_CREATED)


class ApiVerifyEmailView(APIView):
  permission_classes = [permissions.AllowAny]
  throttle_scope = "email_verification"

  def post(self, request):
    email = (request.data.get("email") or "").strip().lower()
    code = (request.data.get("code") or "").strip()
    user = User.objects.filter(email__iexact=email).first()
    otp = EmailVerificationOTP.objects.filter(user=user, used_at__isnull=True, expires_at__gt=timezone.now()).order_by("-created_at").first() if user else None
    if not user or not otp or otp.code_hash != _hash_otp(code):
      return Response({"detail": "Invalid or expired verification code."}, status=status.HTTP_400_BAD_REQUEST)
    otp.used_at = timezone.now()
    otp.save(update_fields=["used_at"])
    user.is_active = True
    user.save(update_fields=["is_active"])
    send_welcome_email(user=user)
    return Response(_auth_payload(user))


class ApiLoginView(APIView):
  permission_classes = [permissions.AllowAny]
  throttle_scope = "login"

  def post(self, request):
    email = (request.data.get("email") or "").strip().lower()
    password = request.data.get("password") or ""
    if get_login_lockout(email, request):
      return Response({"detail": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)
    existing_user = User.objects.filter(email__iexact=email).first()
    if existing_user and not existing_user.is_active:
      return Response({"detail": "Please verify your email before signing in."}, status=status.HTTP_403_FORBIDDEN)
    user = authenticate(request=request, username=email, password=password)
    if not user:
      record_login_failure(email, request)
      return Response({"detail": "Invalid email or password."}, status=status.HTTP_400_BAD_REQUEST)
    clear_login_failures(email, request)
    return Response(_auth_payload(user))
