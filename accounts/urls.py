from allauth.socialaccount.views import signup
from django.urls import path

from .views import *

urlpatterns = [
    path("signup/", signup, name="socialaccount_signup"),
    path("google/", GoogleLogin.as_view(), name="google_login"),
    path("github/", GithubLogin.as_view(), name="github_login"),
]
