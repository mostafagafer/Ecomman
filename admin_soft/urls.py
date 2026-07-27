from django.urls import path
from admin_soft import views
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('', views.landing, name='landing'),
    # path('billing/', views.billing, name='billing'),
    # path('tables/', views.tables, name='tables'),
    path('rtl/', views.rtl, name='rtl'),
    path('vr/', views.vr, name='vr'),

    # Authentication
    path('accounts/login/', views.UserLoginView.as_view(), name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/verify-email/', views.verify_email, name='verify_email'),
    path('accounts/resend-verification-otp/', views.resend_verification_otp, name='resend_verification_otp'),
    path('accounts/password-change/', views.UserPasswordChangeView.as_view(), name='password_change'),
    path('accounts/password-change-done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='accounts/password_change_done.html'
    ), name="password_change_done"),
    path('accounts/password-reset/', views.UserPasswordResetView.as_view(), name='password_reset'),
    path('accounts/password-reset-confirm/<uidb64>/<token>/', 
        views.UserPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/password-reset-done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('accounts/password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    path('api/auth/register/', views.ApiRegisterView.as_view(), name='api_auth_register'),
    path('api/auth/verify-email/', views.ApiVerifyEmailView.as_view(), name='api_auth_verify_email'),
    path('api/auth/login/', views.ApiLoginView.as_view(), name='api_auth_login'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
