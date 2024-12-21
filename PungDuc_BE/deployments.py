import os
from .settings import *
from .settings import BASE_DIR

ALLOWED_HOSTS = [os.environ['HOSTNAME']]
CSRF_TRUSTED_ORIGINS = ['https://' + os.environ['HOSTNAME']]
DEBUG = False
SECRET_KEY = os.environ['SECRET_KEY']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

CONNECTION = os.environ['AZURE_POSTGRESQL_CONNECTIONSTRING']
CONNECTION_STR = {pair.split('=')[0]: pair.split('=')[1] for pair in CONNECTION.split(' ')}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': CONNECTION_STR['db_name'],
        'HOST': CONNECTION_STR['host'],
        'USER': CONNECTION_STR['user'],
        'PASSWORD': CONNECTION_STR['password'],
    }
}

STATIC_ROOT = BASE_DIR/'staticfiles'

SITE_ID = 1

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]


# -------------------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'accounts.CustomUser'

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Gửi email
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
REST_SESSION_LOGIN = False

ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 1
ACCOUNT_EMAIL_CONFIRMATION_AUTHENTICATED_REDIRECT_URL = os.environ["LOGIN_URL"]
PASSWORD_RESET_TIMEOUT = 60 * 60 * 24
PASSWORD_RESET_CONFIRM_REDIRECT_BASE_URL = os.environ["FRONTEND_RESET_PASSWORD_URL"]
LOGIN_URL = os.environ["LOGIN_URL"]
LOGOUT_REDIRECT_URL = os.environ["LOGIN_URL"]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
DEFAULT_FROM_EMAIL = os.environ["EMAIL_HOST_USER"]

# Đăng nhập oauth2
REST_USE_JWT = True
JWT_AUTH_COOKIE = 'PungDuc'
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.environ["GOOGLE_CLIENT_ID"],
            'secret': os.environ["GOOGLE_CLIENT_SECRET"],
            'key': ''
        },
        'SCOPE': [
            'email',
            'profile',
            'openid',
        ],
        'AUTH_PARAMS': {'access_type': 'online'},
        'VERIFY_EMAIL': True
    },
    'github': {
        'APP': {
            'client_id': os.environ["GITHUB_CLIENT_ID"],
            'secret': os.environ["GITHUB_CLIENT_SECRET"]
        },
        'SCOPE': [
            'user:email',
        ],
    },
}
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_LOGOUT_ON_GET = True
LOGIN_REDIRECT_URL = os.environ["CALL_BACK_URL"]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': [
        'rest_framework.pagination.PageNumberPagination'
    ],
    'PAGE_SIZE': 10,
}

REST_AUTH = {
    'LOGIN_SERIALIZER': 'accounts.serializers.CustomLoginSerializer',
    'REGISTER_SERIALIZER': 'accounts.serializers.UserRegistrationSerializer',
    'USER_DETAILS_SERIALIZER': 'accounts.serializers.UserProfileSerializer',
    'PASSWORD_RESET_SERIALIZER': 'accounts.serializers.CustomPasswordResetSerializer',
    'PASSWORD_RESET_CONFIRM_SERIALIZER': 'accounts.serializers.CustomPasswordResetConfirmSerializer',
    'PASSWORD_CHANGE_SERIALIZER': 'accounts.serializers.CustomPasswordChangeSerializer',
    "USE_JWT": True,
    "JWT_AUTH_HTTPONLY": False,
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=3),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CELERY_BROKER_URL = os.environ["CACHE_URL"]
CELERY_ACCEPT_CONTENT = {'application/json'}
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Bangkok'
CELERY_RESULT_BACKEND = os.environ["CACHE_URL"]
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

CELERY_BEAT_SCHEDULE = {
    'send_deadline_notifications_every_hour': {
        'task': 'notifications.tasks.send_deadline_notifications',
        'schedule': timedelta(minutes=1),
    },
    'send_notifications_overdue_tasks': {
        'task': 'notifications.tasks.send_notification_overdue_tasks',
        'schedule': timedelta(minutes=1),
    },
    'create_weekly_report': {
        'task': 'reports.tasks.create_weekly_report',
        'schedule': crontab(minute='0', hour='0', day_of_week='1'),
        # 'schedule': timedelta(seconds=10),
    },
    'create_monthly_report': {
        'task': 'reports.tasks.create_monthly_report',
        'schedule': crontab(minute='0', hour='0', day_of_month='1'),
        # 'schedule': timedelta(seconds=10),
    },
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Bangkok'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
