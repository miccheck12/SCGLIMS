"""Heroku settings and globals."""

from os.path import join, normpath

from base import *

########## FOR WSGI
HEROKU = True
########## END FOR WSGI

########## DEBUG CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
TEMPLATE_DEBUG = DEBUG
########## END DEBUG CONFIGURATION


########## EMAIL CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
########## END EMAIL CONFIGURATION


########## DATABASE CONFIGURATION
# Parse database configuration from $DATABASE_URL
import dj_database_url
DATABASES['default'] = dj_database_url.config()
########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
########## END CACHE CONFIGURATION

########## STATIC CONFIGURATION
#STATIC_ROOT = DJANGO_ROOT + "/static"
BASE_DIR = DJANGO_ROOT
STATIC_ROOT = 'staticfiles'
#STATIC_URL = '/static/'
STATIC_URL = '/lims/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
########## END STATIC CONFIGURATION


########## MORE HEROKU CONFIG
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Allow all host headers
ALLOWED_HOSTS = ['*']

# Set the SECRET_KEY with heroku config:add DJANGO_SECRET_KEY
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
########## END MORE HEROKU CONFIG
