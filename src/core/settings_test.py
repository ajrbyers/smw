# ## GENERIC CONFIG ##

SECRET_KEY = '_%@8*2$*1*i&um4+#a6w(%xqa_19=tfmhu9u-l*7t(a$g(2)wg'

from .settings_dev import *

DEBUG = False
DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'
LOGGING = {}
