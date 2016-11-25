"""
Django settings for smw project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from django.contrib import messages

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
BOOK_DIR = os.path.join(BASE_DIR, 'files', 'books')
PROPOSAL_DIR = os.path.join(BASE_DIR, 'files', 'proposals')
EMAIL_DIR = os.path.join(BASE_DIR, 'files', 'email', 'general')

SITE_ID = 1

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_%@8*2$*1*i&um4+#a6w(%xqa_19=tfmhu9u-l*7t(a$g(2)wg'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

BASE_URL = 'http://localhost:8000/'

ORCID_API_URL = 'http://pub.orcid.org/v1.2_rc7/'
ORCID_REDIRECT_URI = 'http://localhost:8002/login/orcid/'
ORCID_TOKEN_URL = 'https://pub.orcid.org/oauth/token'
ORCID_CLIENT_SECRET = 'insert-client-secret'
ORCID_CLIENT_ID = 'insert-client-id'

# Application definition

INSTALLED_APPS = (
    'flat',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_nose',

    # Django
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

    # 3rd Party
    'bootstrap3',
    'pymarc',
    'debug_toolbar',
    'django_summernote',
    'rest_framework',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',

    # allauth providers
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

ROOT_URLCONF = 'core.urls'

WSGI_APPLICATION = 'core.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'rua',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': '127.0.0.1',
        'PORT': ''
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-gb'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/
STATIC_ROOT = os.path.join(BASE_DIR, 'collected-static')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static-assets'),
)
STATIC_URL = '/static/'

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

# Media
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Over-rides

MESSAGE_TAGS = {
    messages.ERROR: 'danger',
}

LOGIN_REDIRECT_URL = '/user/profile/'
LOGIN_URL = '/login/'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:m'

SESSION_COOKIE_NAME = 'rua_cookie'

SUMMERNOTE_CONFIG = {
    # Using SummernoteWidget - iframe mode
    'iframe': False,  # or set False to use SummernoteInplaceWidget - no iframe mode

    # Using Summernote Air-mode
    'airMode': True,

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

AUTHENTICATION_BACKENDS = (
    # Needed to login by username in Django admin, regardless of `allauth`
    'django.contrib.auth.backends.ModelBackend',

    # `allauth` specific authentication methods, such as login by e-mail
    'allauth.account.auth_backends.AuthenticationBackend',
)

# 1.8 appears confused about where null and blank are required for many to many fields, so we're hiding these warning from the console
SILENCED_SYSTEM_CHECKS = (
    'fields.W340',
)

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

NOSE_ARGS = [
    '--with-coverage',  # activate coverage report
    #  '--with-doctest',  # activate doctest: find and run docstests
    '--verbosity=2',  # verbose output
    '--nocapture',
    '--nologcapture',

    # Run test: python manage.py test --cover-package=(app)

    '--cover-package=core,author,editor,manager,onetasker,review,submission',
    # uncomment to run all tests with 'python manage.py test'

    #    '--with-xunit',    # enable XUnit plugin
    #   '--xunit-file=xunittest.xml',  # the XUnit report file
    #    '--cover-xml',     # produle XML coverage info
    #    '--cover-xml-file=coverage.xml',  # the coverage info file

]