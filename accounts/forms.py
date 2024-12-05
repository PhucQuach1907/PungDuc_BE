from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator


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

        if not token_generator:
            token_generator = default_token_generator

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
