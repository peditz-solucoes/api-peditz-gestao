"""
Django settings for peditz project.

Generated by 'django-admin startproject' using Django 4.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from datetime import timedelta
import os
from pathlib import Path
import time
import environ
import logging.config
env = environ.Env()


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-b3@h@(2)o+=c4nk9j9g33&pz508qc-mbe4w9n)-f#qr#myx!nh'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", False)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG' if DEBUG else 'INFO',
            'propagate': True,
        },
    },
}

logging.config.dictConfig(LOGGING)

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.user',
    'apps.restaurants',
    'apps.financial',
    'apps.inventory',
    'apps.tax_module',
    'apps.delivery',
    # Contrib Apps
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'allauth',
    'allauth.account',
    'dj_rest_auth.registration',
    'corsheaders',
    'localflavor',
    'phonenumber_field',
    'django_admin_listfilter_dropdown',
    'django_filters',

]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

CSRF_TRUSTED_ORIGINS = ['https://peditz-gestao-production.up.railway.app', 'http://localhost:5173', 'https://api-hml.peditz.com', 'https://api.peditz.com']

CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = 'peditz.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'peditz.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
import dj_database_url

DATABASES = {
    "default": dj_database_url.config(default='sqlite:///db.sqlite3')
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'pt-BR'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/



# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'



REST_SESSION_LOGIN = True
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
SITE_ID = 1
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'email'
ACCOUNT_USERNAME_REQUIRED = False

REST_USE_JWT = True

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        # 'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema'
}

REST_AUTH_REGISTER_SERIALIZERS = {
    'REGISTER_SERIALIZER': 'apps.user.api.serializers.UserSerializer'
}
REST_AUTH_LOGIN_SERIALIZERS = {
    'LOGIN_SERIALIZER': 'apps.user.api.serializers.UserLoginSerializer'
}

SWAGGER_SETTINGS = {
    'LOGIN_URL': 'rest_login',
    'LOGOUT_URL': 'rest_logout',
}

# TODO: Use a white list in the real world.
CORS_ORIGIN_ALLOW_ALL = True

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)

CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)


# CUSTOM USERS
AUTH_USER_MODEL = 'user.user'


REST_AUTH = {
    'USE_JWT': True,
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',

    'REST_USE_JWT': True,
    'REGISTER_SERIALIZER': 'apps.user.api.serializers.UserSerializer',
    'LOGIN_SERIALIZER': 'apps.user.api.serializers.UserLoginSerializer',
    'CSRF_COOKIE_SECURE': False
}
JWT_AUTH_COOKIE = 'auth'
CSRF_COOKIE_SECURE = False
JWT_AUTH_COOKIE_USE_CSRF = False
# DO SPACES

expires = time.time() + 6 * 24 * 3600 # 6 days from now

DEFAULT_FILE_STORAGE = 'peditz.storage_backends.CustomS3Boto3Storage'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS', '')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET', '')
AWS_STORAGE_BUCKET_NAME = os.environ.get('BUCKET_NAME', '')
AWS_S3_ENDPOINT_URL = os.environ.get('AWS_S3_ENDPOINT_URL', '')
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
    "ACL": "public-read"
}
AWS_LOCATION = os.environ.get('AWS_LOCATION', '')

CKEDITOR_UPLOAD_PATH = "site/uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"

THUMBNAIL_FORCE_OVERWRITE = True
THUMBNAIL_QUALITY = 80



JWT_AUTH = {
    # how long the original token is valid for
    'JWT_EXPIRATION_DELTA': timedelta(seconds=1296000),

    # allow refreshing of tokens
    'JWT_ALLOW_REFRESH': True,

    # this is the maximum time AFTER the token was issued that
    # it can be refreshed.  exprired tokens can't be refreshed.
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=7),
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),
}