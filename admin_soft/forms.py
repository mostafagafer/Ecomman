from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
# from .models import Profile


class RegistrationForm(UserCreationForm):
  email = forms.EmailField(widget=forms.EmailInput(attrs={
      'class': 'form-control',
      'placeholder': 'Email'
  }))
  password1 = forms.CharField(
      label=_("Password"),
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}),
  )
  password2 = forms.CharField(
      label=_("Password Confirmation"),
      widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password Confirmation'}),
  )

  class Meta:
    model = User
    fields = ('email', )

    widgets = {
      'email': forms.EmailInput(attrs={
          'class': 'form-control',
          'placeholder': 'Email'
      })
    }

  def clean_email(self):
    email = (self.cleaned_data.get('email') or '').strip().lower()
    if User.objects.filter(email__iexact=email).exists():
      raise forms.ValidationError("This email is already registered.")
    return email

  def save(self, commit=True):
    user = super().save(commit=False)
    user.email = self.cleaned_data['email']
    user.username = self.cleaned_data['email']
    user.is_active = False
    if commit:
      user.save()
    return user

        
class LoginForm(AuthenticationForm):
  username = forms.EmailField(label=_("Email"), widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Email"}))
  password = forms.CharField(
      label=_("Password"),
      strip=False,
      widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Password"}),
  )

  error_messages = {
      "invalid_login": _("Please enter a correct email and password."),
      "inactive": _("Please verify your email before signing in."),
  }

  def clean(self):
    email = (self.cleaned_data.get("username") or "").strip().lower()
    password = self.cleaned_data.get("password")
    if email and password:
      self.user_cache = authenticate(self.request, username=email, password=password)
      if self.user_cache is None:
        raise self.get_invalid_login_error()
      self.confirm_login_allowed(self.user_cache)
    return self.cleaned_data


class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control'
    }))

class UserSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")
    

class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Old Password'
    }), label='Old Password')
    new_password1 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'New Password'
    }), label="New Password")
    new_password2 = forms.CharField(max_length=50, widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Confirm New Password'
    }), label="Confirm New Password")
