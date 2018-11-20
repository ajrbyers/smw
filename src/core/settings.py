from configparser import ConfigParser
import os

from django.contrib import messages


# ## GENERIC CONFIG ##

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')

CODE = os.getenv('CODE')

ADMIN_USERNAME = os.getenv('DJANGO_ADMIN_USERNAME', 'tech')
ADMIN_PASSWORD = os.getenv('DJANGO_ADMIN_PASSWORD')
ADMIN_EMAIL = os.getenv('DJANGO_ADMIN_EMAIL')

# Allow static files to be served by uwsgi/gunicorn?
INCLUDE_STATIC_FILE_URLCONFS = False

SITE_ID = 1

ROOT_URLCONF = 'core.urls'

WSGI_APPLICATION = 'core.wsgi.application'

LOGIN_REDIRECT_URL = '/user/profile/'
LOGIN_URL = '/login/'

INSTALLED_APPS = (
    'flat',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
    'submission',
    'manager',
    'review',
    'api',
    'cron',
    'revisions',
    'author',
    'onetasker',
    'editor',
    'swiftsubmit',
    'editorialreview',
    'bootstrap3',
    'django_summernote',
    'rest_framework',
    'pymarc',
    'storages',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.orcid',
    'allauth.socialaccount.providers.twitter',
    'raven.contrib.django.raven_compat',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.Roles',
    'core.middleware.Version',
)

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',
    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Django 1.8 appears confused about where null and blank are required for
# ManyToMany fields, so we're hiding these warning from the console.
SILENCED_SYSTEM_CHECKS = (
    'fields.W340',
)


# ## SUMMERNOTE ##

SUMMERNOTE_CONFIG = {
    # Using SummernoteWidget - iframe mode.
    'iframe': False,  # If False: use SummernoteInplaceWidget - no iframe mode.
    'airMode': True,  # Using Summernote Air-mode.
    # Use native HTML tags (`<b>`, `<i>`, ...) instead of style attributes
    # (Firefox, Chrome only)
    'styleWithTags': True,
    # Set text direction : 'left to right' is default.
    'direction': 'ltr',
    # Change editor size
    'width': '100%',
    'height': '480',
    # Need authentication while uploading attachments.
    'attachment_require_authentication': True,
}


# ## CACHE ##

REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '{host}:{port}'.format(host=REDIS_HOST, port=REDIS_PORT)
    }
}


# ## INTERNATIONALISATION ##

LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
DATE_FORMAT = '%d %b, %Y'
DATETIME_FORMAT = '%d %b, %Y %H:%M'


# ## STATIC FILES ##

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
STATIC_ROOT = os.path.join(BASE_DIR, 'collected-static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static-assets'),
)

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
SETTINGS_MEDIA_DIR = os.path.join('files', 'media', 'settings')
FORM_DIR = os.path.join('files', 'forms')
PROPOSAL_DIR = os.path.join('files', 'proposals')
BOOK_DIR = os.path.join('files', 'books')
EMAIL_DIR = os.path.join('files', 'email', 'general')

MEDIA_URL = '/media/'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Already defined Django-related contexts here
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.template.context_processors.request",
                "django.contrib.messages.context_processors.messages",
                "core.context_processors.press",
                "core.context_processors.task_count",
                "core.context_processors.review_assignment_count",
                "core.context_processors.onetasker_task_count",
                "core.context_processors.author_task_count",
                "core.context_processors.switch_account",
                "core.context_processors.roles",
                "core.context_processors.domain",
            ],
        },
    },
]


# ## VERSION ##

# Updated, committed and tagged using 'bumpversion [major | minor | patch]'
# run on master branch
RUA_VERSION = '3.0.9'


# ## LOGGING ##

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
    },
}


# ## DATABASE ##

DATABASES = {
    'default': {
        'ENGINE': os.getenv(
            'DATABASE_ENGINE',
            'django.db.backends.postgresql_psycopg2'
        ),
        'NAME': os.getenv('DATABASE_NAME', CODE),
        'USER': os.getenv('DATABASE_USER', 'root'),
        'PASSWORD': os.getenv('DATABASE_PASS', ''),
        'HOST': os.getenv('DATABASE_HOST', '127.0.0.1'),
        'PORT': os.getenv('DATABASE_PORT', '5432')
    }
}


# ## EXTERNAL SERVICES ##

# ORCID

ORCID_API_URL = os.getenv('ORCID_API_URL', 'http://pub.orcid.org/v1.2_rc7/')
ORCID_REDIRECT_URI = os.getenv(
    'ORCID_REDIRECT_URI',
    'http://localhost:8002/login/orcid/'
)
ORCID_TOKEN_URL = os.getenv(
    'ORCID_TOKEN_URL',
    'https://pub.orcid.org/oauth/token'
)
ORCID_CLIENT_SECRET = os.getenv('ORCID_CLIENT_SECRET')
ORCID_CLIENT_ID = os.getenv('ORCID_CLIENT_ID')

# AMAZON S3
AWS_DEFAULT_ACL = None
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_S3_OBJECT_PARAMETERS = {"CacheControl": "max-age=86400"}
AWS_STORAGE_BUCKET_NAME = os.getenv(
    'AWS_STORAGE_BUCKET_NAME',
    'service-rua'
)
AWS_S3_CUSTOM_DOMAIN = os.getenv(
    'AWS_S3_CUSTOM_DOMAIN',
    f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com',
)
AWS_LOCATION = CODE

if AWS_LOCATION:
    AWS_STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/'
else:
    AWS_STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'

# EMAIL

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_USE_TLS = bool(os.getenv('EMAIL_USE_TLS', True))
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.mailgun.org')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'postmaster@ubiquity.press')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))

# SENTRY

SENTRY_DSN = os.getenv(
    'SENTRY_DSN',
    'https://6f4e629b9384499ea7d6aaa72c820839:'
    '33c1f6db04914ee7bf7569f1f3e9cb61@sentry.ubiquity.press/5'
)
config_file = ConfigParser()
config_file.read('sentry_version.ini')
SENTRY_RELEASE = config_file.get('sentry', 'version', fallback='ERROR')

RAVEN_CONFIG = {
    'dsn': SENTRY_DSN,
    'release': SENTRY_RELEASE,
    'environment': 'production'
}
