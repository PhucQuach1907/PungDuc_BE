import re

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import PasswordResetSerializer, LoginSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction, IntegrityError
from django.utils.http import urlsafe_base64_decode
from requests import Response
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError

from .forms import CustomPasswordResetForm
from .models import CustomUser


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name')
        read_only_fields = ['id', 'email']


class CustomLoginSerializer(LoginSerializer):
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if not email or not password:
            raise serializers.ValidationError({"error": "Yêu cầu nhập đầy đủ email và mật khẩu!"})

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"error": "Tài khoản không tồn tại!"})

        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError({"error": "Mật khẩu không đúng!"})

        if not user.is_active:
            raise serializers.ValidationError({"error": "Tài khoản này đã bị vô hiệu hóa!"})

        email_address = EmailAddress.objects.filter(user=user, email=email).first()
        if not email_address or not email_address.verified:
            raise serializers.ValidationError(
                {"error": "Tài khoản chưa xác minh email."})

        attrs['user'] = user
        return attrs


class UserRegistrationSerializer(RegisterSerializer):
    email = serializers.EmailField()
    username = None
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError({"error": "Email này đã được sử dụng."})
        return value

    def validate_password1(self, value):
        if len(value) < 8:
            raise serializers.ValidationError({"error": "Mật khẩu phải có ít nhất 8 ký tự."})

        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError({"error": "Mật khẩu phải chứa ít nhất một chữ cái."})

        if not re.search(r'\d', value):
            raise serializers.ValidationError({"error": "Mật khẩu phải chứa ít nhất một chữ số."})

        return value

    def validate(self, attrs):
        password1 = attrs.get('password1')
        password2 = attrs.get('password2')

        if password1 != password2:
            raise serializers.ValidationError({"error": "Mật khẩu và xác nhận mật khẩu không khớp."})

        return attrs

    @transaction.atomic
    def save(self, request):
        try:
            user = super().save(request)
            user.email = self.validated_data.get('email')
            user.first_name = self.validated_data.get('first_name')
            user.last_name = self.validated_data.get('last_name')
            user.save()

            return user
        except IntegrityError as e:
            if 'accounts_customuser_email_key' in str(e):
                raise ValidationError({"message": "Email này đã được sử dụng."})
            raise e


class CustomPasswordResetSerializer(PasswordResetSerializer):
    password_reset_form_class = CustomPasswordResetForm

    def validate_email(self, value):
        try:
            user = CustomUser.objects.get(email=value)
            if SocialAccount.objects.filter(user=user).exists():
                raise serializers.ValidationError(
                    {"error": "Tài khoản được tạo bằng OAuth2 không thể đặt lại mật khẩu."}
                )
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError(
                {"error": "Không tìm thấy tài khoản với email này."}
            )

        self.reset_form = self.password_reset_form_class(data=self.initial_data)
        if not self.reset_form.is_valid():
            raise serializers.ValidationError(self.reset_form.errors)

        return value


class CustomPasswordResetConfirmSerializer(serializers.Serializer):
    password1 = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        request = self.context.get('request')
        uidb64 = self.context.get('view').kwargs.get('uidb64')
        token = self.context.get('view').kwargs.get('token')

        print("Token: ", token)
        print("uidb64: ", uidb64)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            self.user = CustomUser.objects.get(pk=uid)
        except (ValueError, CustomUser.DoesNotExist):
            raise serializers.ValidationError({"error": "Invalid UID"})

        if not default_token_generator.check_token(self.user, token):
            raise serializers.ValidationError({"error": "Invalid or expired token"})

        if attrs['password1'] != attrs['password2']:
            raise serializers.ValidationError({"error": "Passwords do not match"})

        return attrs

    def save(self):
        password = self.validated_data['password1']
        self.user.set_password(password)
        self.user.save()


class CustomPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError({"error": "Mật khẩu mới phải có ít nhất 8 ký tự."})

        if not re.search(r'[A-Za-z]', value):
            raise serializers.ValidationError({"error": "Mật khẩu phải chứa ít nhất một chữ cái."})

        if not re.search(r'\d', value):
            raise serializers.ValidationError({"error": "Mật khẩu phải chứa ít nhất một chữ số."})

        return value

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_new_password = attrs.get('confirm_new_password')

        if new_password != confirm_new_password:
            raise serializers.ValidationError({"error": "Mật khẩu mới và xác nhận mật khẩu không khớp."})

        return attrs

    def save(self):
        user = self.context.get('request').user
        password = self.validated_data['new_password']
        user.set_password(password)
        user.save()
        return user
