"""
URL configuration for PungDuc_BE project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from allauth.account.views import ConfirmEmailView, EmailVerificationSentView
from dj_rest_auth.views import PasswordResetConfirmView, UserDetailsView, PasswordChangeView
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import CustomRegisterView, CustomResetPasswordView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/registration/', CustomRegisterView.as_view(), name='registration'),
    path('api/auth/registration/account-confirm-email/<str:key>/', ConfirmEmailView.as_view()),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/auth/registration/verify-email/', EmailVerificationSentView.as_view()),
    path('api/auth/password/reset/', CustomResetPasswordView.as_view(), name='password_reset'),
    path('api/auth/password/reset/confirm/<slug:uidb64>/<slug:token>/',
         PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('api/auth/password/change/', PasswordChangeView.as_view(), name='password_change'),
    path('api/auth/social/', include('accounts.urls')),
    path('api/users/', UserDetailsView.as_view(), name='user_details'),
    path('api/tasks/', include('tasks.urls')),
]
