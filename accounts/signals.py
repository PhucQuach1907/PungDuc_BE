from allauth.account.signals import email_confirmed, user_signed_up, user_logged_in
from allauth.socialaccount.signals import social_account_added
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    user = get_user_model()
    if not user.objects.filter(is_superuser=True).exists():
        user.objects.create_superuser(
            email='admin@admin.com',
            password='1'
        )


@receiver(email_confirmed)
def email_confirmed(request, email_address, **kwargs):
    user = email_address.user
    user.email_verified = True

    user.save()


@receiver(user_signed_up)
def user_signed_up_handler(request, user, sociallogin=None, **kwargs):
    if sociallogin is not None:
        social_account = sociallogin.account
        user.oauth_provider = social_account.provider
        user.oauth_id = social_account.uid
    user.save()


@receiver(user_logged_in)
def user_logged_in_handler(sender, request, user, **kwargs):
    print(f'User {user.email} logged in')

    if user.socialaccount_set.filter(provider='google').exists():
        print(f'User {user.email} logged in via Google')
