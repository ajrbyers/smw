# ## GENERIC CONFIG ##

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_%@8*2$*1*i&um4+#a6w(%xqa_19=tfmhu9u-l*7t(a$g(2)wg'

from base_settings import *

# SECURITY WARNING: don't run with debug turned on in production!
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


# ## DATABASE ##

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


# ## TESTS ##

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
TEST_WITHOUT_MIGRATIONS_COMMAND = 'django_nose.management.commands.test.Command'

NOSE_ARGS = [
    '--with-coverage',  # activate coverage report
    #  '--with-doctest',  # activate doctest: find and run docstests
    '--verbosity=2',   # verbose output
    '--nocapture',
    '--nologcapture',

    # Run test: python manage.py test --cover-package=(app)
    '--cover-package=core,author,editor,manager,onetasker,review,submission',  # uncomment to run all tests with 'python manage.py test'

    #    '--with-xunit',    # enable XUnit plugin
    #   '--xunit-file=xunittest.xml',  # the XUnit report file
    #    '--cover-xml',     # produle XML coverage info
    #    '--cover-xml-file=coverage.xml',  # the coverage info file
]


# ## EXTERNAL SERVICES ##

ORCID_API_URL = 'http://pub.orcid.org/v1.2_rc7/'
ORCID_REDIRECT_URI = 'http://localhost:8002/login/orcid/'
ORCID_TOKEN_URL = 'https://pub.orcid.org/oauth/token'
ORCID_CLIENT_SECRET = 'insert-client-secret'
ORCID_CLIENT_ID = 'insert-client-id'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
