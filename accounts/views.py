import requests
from allauth.account import app_settings as allauth_account_settings
from allauth.account.internal.flows.logout import logout
from allauth.account.models import EmailAddress
from allauth.account.utils import complete_signup, send_email_confirmation
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView, RegisterView
from dj_rest_auth.views import PasswordResetView
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.utils.http import urlsafe_base64_decode
from django.utils.timezone import now
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from PungDuc_BE.settings import env
from .helpers import CustomTokenGenerator
from .models import CustomUser
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


class ResendEmailConfirmationView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.user.email
        try:
            email_address = EmailAddress.objects.get(user=request.user, email=email)
            if email_address.verified:
                return Response({"message": "Email đã được xác minh."}, status=400)
            send_email_confirmation(request, request.user)
            return Response({"message": "Email xác thực đã được gửi lại."})
        except EmailAddress.DoesNotExist:
            return Response({"message": "Không tìm thấy địa chỉ email."}, status=400)


class CustomResetPasswordView(PasswordResetView):
    permission_classes = (AllowAny,)
    serializer_class = CustomPasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()
        return Response(
            {"message": "Email đặt lại mật khẩu đã được gửi thành công."},
            status=status.HTTP_200_OK
        )


class CustomPasswordResetConfirmView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        try:
            uidb64 = kwargs.get("uidb64")
            token = kwargs.get("token")

            uid = urlsafe_base64_decode(uidb64).decode()
            user = CustomUser.objects.get(pk=uid)
            custom_token_generator = CustomTokenGenerator()
            token_is_valid = custom_token_generator.check_token(user, token)

            if not token_is_valid:
                if token in custom_token_generator.make_token(user):
                    return Response(
                        {"error": "Expired token. Please request a new password reset."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                else:
                    return Response(
                        {"error": "Invalid token. The reset link may be incorrect."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

            password1 = request.data.get("password1")
            password2 = request.data.get("password2")

            if not password1 or not password2:
                return Response(
                    {"error": "Both password1 and password2 are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if password1 != password2:
                return Response(
                    {"error": "Passwords do not match."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                validate_password(password1, user)
            except ValidationError as e:
                return Response(
                    {"error": e.messages},
                    status=status.HTTP_400_BAD_REQUEST
                )

            user.set_password(password1)
            user.last_login = now()
            user.save()

            return Response(
                {"message": "Password reset successful. You can now log in with your new password."},
                status=status.HTTP_200_OK
            )

        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User does not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = env("CALL_BACK_URL")
    client_class = OAuth2Client
    permission_classes = (AllowAny,)


class ProxyGoogleTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            code = request.data.get("code")
            redirect_uri = request.data.get("redirect_uri")

            if not code or not redirect_uri:
                return Response(
                    {"error": "Missing 'code' or 'redirect_uri' in the request."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            payload = {
                "code": code,
                "client_id": env("GOOGLE_CLIENT_ID"),
                "client_secret": env("GOOGLE_CLIENT_SECRET"),
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            }

            google_response = requests.post("https://oauth2.googleapis.com/token", data=payload)

            if google_response.status_code == 200:
                return JsonResponse(google_response.json())
            else:
                return JsonResponse(
                    {"error": "Failed to fetch Google token", "details": google_response.json()},
                    status=google_response.status_code,
                )

        except Exception as e:
            return JsonResponse(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GithubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = env("CALL_BACK_URL")
    client_class = OAuth2Client
