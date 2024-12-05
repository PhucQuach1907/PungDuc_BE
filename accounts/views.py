from allauth.account import app_settings as allauth_account_settings
from allauth.account.internal.flows.logout import logout
from allauth.account.utils import complete_signup
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView, RegisterView
from dj_rest_auth.views import PasswordResetView
from rest_framework import status
from rest_framework.response import Response

from .serializers import CustomPasswordResetSerializer


class CustomRegisterView(RegisterView):
    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {"message": "Đăng ký thành công! Vui lòng kiểm tra email để xác nhận."},
            status=status.HTTP_201_CREATED
        )

    def get_response_data(self, user):
        return {"detail": "Đăng ký thành công. Vui lòng đăng nhập."}

    def perform_create(self, serializer):
        user = serializer.save(self.request)

        complete_signup(
            self.request._request, user,
            allauth_account_settings.EMAIL_VERIFICATION,
            None,
        )

        logout(self.request._request)


class CustomResetPasswordView(PasswordResetView):
    serializer_class = CustomPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(
            {"message": "Email đặt lại mật khẩu đã được gửi thành công."},
            status=status.HTTP_200_OK
        )


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "https://www.youtube.com/"
    client_class = OAuth2Client


class GithubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = "https://www.youtube.com/"
    client_class = OAuth2Client
