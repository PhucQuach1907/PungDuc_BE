from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from PungDuc_BE.settings import env
from accounts.helpers import CustomTokenGenerator


class CustomPasswordResetForm(PasswordResetForm):
    def save(self, domain_override=None,
             subject_template_name=None,
             email_template_name=None,
             html_email_template_name=None,
             use_https=False, token_generator=None,
             from_email=None, request=None, extra_email_context=None):
        email_template_name = 'registration/password_reset_email.txt'
        html_email_template_name = 'registration/password_reset_email.html'
        subject_template_name = 'registration/password_reset_subject.txt'

        custom_token_generator = CustomTokenGenerator()
        token_generator = custom_token_generator

        print(token_generator)

        frontend_reset_url = env('FRONTEND_RESET_PASSWORD_URL')

        if extra_email_context is None:
            extra_email_context = {}

        extra_email_context['frontend_reset_url'] = frontend_reset_url

        super().save(
            domain_override=domain_override,
            subject_template_name=subject_template_name,
            email_template_name=email_template_name,
            html_email_template_name=html_email_template_name,
            use_https=use_https,
            token_generator=token_generator,
            from_email=from_email,
            request=request,
            extra_email_context=extra_email_context
        )
