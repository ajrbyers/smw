# ## GENERIC CONFIG ##

SECRET_KEY = '_%@8*2$*1*i&um4+#a6w(%xqa_19=tfmhu9u-l*7t(a$g(2)wg'

from base_settings import *

DEBUG = True

ALLOWED_HOSTS = [
    'localhost',
]

BASE_URL = 'http://localhost:8000/'

SESSION_COOKIE_NAME = 'rua_cookie'

INSTALLED_APPS += (
    'test_without_migrations',
    'debug_toolbar',
)

# Allow static files to be served by uwsgi/gunicorn?
INCLUDE_STATIC_FILE_URLCONFS = True

# ## DATABASE ##

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.getenv('DATABASE_NAME', 'rua'),
        'USER': os.getenv('DATABASE_USER', 'root'),
        'PASSWORD': os.getenv('DATABASE_PASS', ''),
        'HOST': os.getenv('DATABASE_HOST', '127.0.0.1'),
        'PORT': os.getenv('DATABASE_PORT', '3306')
    }
}


# ## EXTERNAL SERVICES ##

ORCID_API_URL = 'http://pub.orcid.org/v1.2_rc7/'
ORCID_REDIRECT_URI = 'http://localhost:8002/login/orcid/'
ORCID_TOKEN_URL = 'https://pub.orcid.org/oauth/token'
ORCID_CLIENT_SECRET = 'insert-client-secret'
ORCID_CLIENT_ID = 'insert-client-id'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
