import os

from django.contrib import messages

# ## GENERIC CONFIG ##

TECH_EMAIL = 'tech@ubiquitypress.com'

ADMINS = (
    ('UP Tech', TECH_EMAIL)
)
# Username of upadmin
INTERNAL_USER = 'tech'


# Allow static files to be served by uwsgi/gunicorn?
INCLUDE_STATIC_FILE_URLCONFS = False

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
RUA_VERSION = '1.9.12'


# ## EXTERNAL SERVICES ##

ORCID_API_URL = 'http://pub.orcid.org/v1.2_rc7/'
ORCID_REDIRECT_URI = 'http://localhost:8002/login/orcid/'
ORCID_TOKEN_URL = 'https://pub.orcid.org/oauth/token'
ORCID_CLIENT_SECRET = 'insert-client-secret'
ORCID_CLIENT_ID = 'insert-client-id'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

SESSION_COOKIE_NAME = 'rua_cookie'
