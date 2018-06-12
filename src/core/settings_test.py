# ## GENERIC CONFIG ##

SECRET_KEY = '_%@8*2$*1*i&um4+#a6w(%xqa_19=tfmhu9u-l*7t(a$g(2)wg'

from settings_dev import *

# ## DATABASE ##

DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.getenv('DATABASE_NAME', 'rua'),
        'USER': os.getenv('DATABASE_USER', 'root'),
        'PASSWORD': os.getenv('DATABASE_PASS', ''),
        'HOST': os.getenv('DATABASE_HOST', 'db'),
        'PORT': os.getenv('DATABASE_PORT', '3306')
    }
}
