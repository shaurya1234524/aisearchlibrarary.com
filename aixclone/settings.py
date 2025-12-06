from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
import os
import environ
import dj_database_url
from dotenv import load_dotenv
# Application definition
AWS_STORAGE_BUCKET_NAME ='shaurya1234512'
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % AWS_STORAGE_BUCKET_NAME
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_FILE_OVERWRITE = True
load_dotenv()
env = environ.Env()
environ.Env.read_env()

SECRET_KEY = 'your-secret-key'

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tools',
    'aixclone',
]
LOGOUT_REDIRECT_URL = 'home'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'aixclone.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR/'templates'],
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

WSGI_APPLICATION = 'aixclone.wsgi.application'

import dj_database_url
DATABASES={
    'default':dj_database_url.parse(env('DATABASE_URL'))
}

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

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/login/'          # redirect to login if @login_required
LOGIN_REDIRECT_URL = '/'       # redirect after login
LOGOUT_REDIRECT_URL = '/'      # redirect after logout



# Development: Use local storage for static files
# Production: Uncomment the S3 storage below
STORAGES = {
    "default": {
        "BACKEND": "tools.storage.MediaStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

# Local development URLs
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / "tools" / "static"]
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Use local filesystem for uploaded media in development
if DEBUG:
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
else:
    # In production, use S3 for media (keep existing STORAGES/S3 config)
    DEFAULT_FILE_STORAGE = 'tools.storage.MediaStorage'

# Production: Uncomment below for S3 storage
# STORAGES = {
#     "default": {
#         "BACKEND": "tools.storage.MediaStorage",
#     },
#     "staticfiles": {
#         "BACKEND": "tools.storage.StaticStorage",
#     },
# }
# STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
# MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
# STATICFILES_DIRS = [BASE_DIR / "tools" / "static"]
