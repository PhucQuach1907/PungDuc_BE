from allauth.socialaccount.views import signup
from django.urls import path

from .views import *

urlpatterns = [
    path("signup/", signup, name="socialaccount_signup"),
    path("google/", GoogleLogin.as_view(), name="google_login"),
    path("google-proxy/", ProxyGoogleTokenView.as_view(), name="proxy_google_token"),
    path("github/", GithubLogin.as_view(), name="github_login"),
    path("github-proxy/", GitHubOAuthProxyView.as_view(), name="github_proxy"),
]
