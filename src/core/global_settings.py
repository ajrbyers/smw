import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

INSTALLED_APPS = (
    'flat',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

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
    #'debug_toolbar',
    'django_summernote',
    'rest_framework',
    'pymarc',
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
            ],
        },
    },
]

TECH_EMAIL = 'tech@ubiquitypress.com'
ADMINS = (
    ('Andy Byers', 'andy.byers@ubiquitypress.com'),
    ('Mauro Sanchez', 'mauro.sanchez@ubiquitypress.com'),
    ('UP Tech', 'tech@ubiquitypress.com')
)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}