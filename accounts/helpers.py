from hashlib import sha256

from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from jwt.utils import force_bytes


class CustomTokenGenerator(PasswordResetTokenGenerator):
    def make_token(self, user):
        uid = urlsafe_base64_encode(force_bytes(str(user.pk)))
        email_hash = sha256(user.email.encode()).hexdigest()
        return f"{uid}-{email_hash}"

    def check_token(self, user, token):
        try:
            uid, email_hash = token.split("-")
            expected_uid = urlsafe_base64_encode(force_bytes(str(user.pk)))
            expected_email_hash = sha256(user.email.encode()).hexdigest()
            return uid == expected_uid and email_hash == expected_email_hash
        except ValueError:
            return False
