import os

from django.contrib import messages

import raven


# ## GENERIC CONFIG ##

TECH_EMAIL = 'tech@ubiquitypress.com'

ADMINS = (
    ('UP Tech', TECH_EMAIL)
)

DEBUG = False  # SECURITY WARNING: don't run with debug turned on in production!

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

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.Roles',
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

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
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
                "django.core.context_processors.debug",
                "django.core.context_processors.i18n",
                "django.core.context_processors.media",
                "django.core.context_processors.static",
                "django.core.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.core.context_processors.request",
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
RUA_VERSION = '1.2.1'


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

SENTRY_RELEASE = (
    '{main}-{sha}'.format(
        main=RUA_VERSION,
        sha=raven.fetch_git_sha(
            os.path.join(
                '/',
                *os.path.dirname(os.path.realpath(__file__)).split('/')[:-2]
            )
        )
    )
)

RAVEN_CONFIG = {  # Sentry.
    'dsn': 'https://6f4e629b9384499ea7d6aaa72c820839:'
           '33c1f6db04914ee7bf7569f1f3e9cb61@sentry.ubiquity.press/5',
    'release': SENTRY_RELEASE
}


# ## EXTERNAL SERVICES ##

ORCID_API_URL = 'http://pub.orcid.org/v1.2_rc7/'
ORCID_REDIRECT_URI = 'http://localhost:8002/login/orcid/'
ORCID_TOKEN_URL = 'https://pub.orcid.org/oauth/token'
ORCID_CLIENT_SECRET = '6d1677b8-25c6-4d42-8a8d-e77a0ced56c6'
ORCID_CLIENT_ID = 'APP-VXH2IGZ6ZH7Q71L9'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'postmaster@ubiquity.press'
EMAIL_HOST_PASSWORD = '4910364428769ec9a64fbcee94bd5d17'  # Fake API key.
EMAIL_PORT = 587
