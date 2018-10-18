import os

from django.contrib import messages


# ## GENERIC CONFIG ##

TECH_EMAIL = os.getenv('TECH_EMAIL', 'tech@ubiquitypress.com')

ADMINS = (
    ('UP Tech', TECH_EMAIL)
)

# Username of upadmin
INTERNAL_USER = 'tech'

DEBUG = False  # SECURITY WARNING: don't run with debug turned on in production!

# Allow static files to be served by uwsgi/gunicorn?
INCLUDE_STATIC_FILE_URLCONFS = False

SITE_ID = 1

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BOOK_DIR = os.path.join(BASE_DIR, 'files', 'books')
PROPOSAL_DIR = os.path.join(BASE_DIR, 'files', 'proposals')
EMAIL_DIR = os.path.join(BASE_DIR, 'files', 'email', 'general')

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
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',
    'allauth.socialaccount.providers.google',
    'allauth.socialaccount.providers.orcid',
    'allauth.socialaccount.providers.twitter',
)

MIDDLEWARE= (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
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
REDIS_PORT = int(os.getenv('REDIS_PORT'), 6379)

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

STATIC_ROOT = os.path.join(BASE_DIR, 'collected-static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static-assets'),
)
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
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
RUA_VERSION = '1.9.9'


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
    },
    'loggers': {
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
    },
}

SENTRY_RELEASE = 'please_use_different_django_settings_file'
SENTRY_DSN = os.getenv('SENTRY_DSN')


# ## EXTERNAL SERVICES ##

ORCID_API_URL = os.getenv('ORCID_API_URL', 'http://pub.orcid.org/v1.2_rc7/')
ORCID_REDIRECT_URI = os.getenv(
    'ORCID_REDIRECT_URI',
    'http://localhost:8002/login/orcid/'
)
ORCID_TOKEN_URL = os.getenv(
    'ORCID_TOKEN_URL',
    'https://pub.orcid.org/oauth/token'
)
ORCID_CLIENT_SECRET = os.getenv(
    'ORCID_CLIENT_SECRET',
    '6d1677b8-25c6-4d42-8a8d-e77a0ced56c6'
)
ORCID_CLIENT_ID = os.getenv(
    'ORCID_CLIENT_ID',
    'APP-VXH2IGZ6ZH7Q71L9'
)

EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend'
)
EMAIL_USE_TLS = bool(os.getenv('EMAIL_USE_TLS', True))
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.mailgun.org')
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'postmaster@ubiquity.press')
EMAIL_HOST_PASSWORD = os.getenv(
    'EMAIL_HOST_PASSWORD',
    '4910364428769ec9a64fbcee94bd5d17'  # Fake API key.
)
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
