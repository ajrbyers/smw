# ## GENERIC CONFIG ##

from .settings import *

SECRET_KEY = '_%@8*2$*1*i&um4+#a6w(%xqa_19=tfmhu9u-l*7t(a$g(2)wg'

DEBUG = True

ALLOWED_HOSTS = [
    host.strip() for host in
    os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost').split(',')
]

SESSION_COOKIE_NAME = 'rua_cookie'

STATIC_URL = '/static/'

MIDDLEWARE += 'debug_toolbar.middleware.DebugToolbarMiddleware',
INSTALLED_APPS += 'debug_toolbar',


# ## DATABASE ##

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE', 'django.db.backends.postgresql_psycopg2'),
        'NAME': os.getenv('DATABASE_NAME', 'rua'),
        'USER': os.getenv('DATABASE_USER', 'root'),
        'PASSWORD': os.getenv('DATABASE_PASS', ''),
        'HOST': os.getenv('DATABASE_HOST', '127.0.0.1'),
        'PORT': os.getenv('DATABASE_PORT', '5432')
    }
}


# ## EXTERNAL SERVICES ##

RAVEN_CONFIG = None
SENTRY_RELEASE = None
SENTRY_DSN = None

ORCID_API_URL = 'http://pub.orcid.org/v1.2_rc7/'
ORCID_REDIRECT_URI = 'http://localhost:8002/login/orcid/'
ORCID_TOKEN_URL = 'https://pub.orcid.org/oauth/token'
ORCID_CLIENT_SECRET = 'insert-client-secret'
ORCID_CLIENT_ID = 'insert-client-id'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'