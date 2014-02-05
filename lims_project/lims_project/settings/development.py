"""Development settings and globals."""

from os.path import join, normpath

from base import *

########## THIRD PARTY IMPORTS
import ldap
import logging
from django_auth_ldap.config import LDAPSearch, PosixGroupType
########## END THIRD PARTY IMPORTS

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
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'django',
        'USER': 'django',
        'PASSWORD': 'django',
        'HOST': 'localhost',
        'PORT': '',
    }
}
########## END DATABASE CONFIGURATION


########## CACHE CONFIGURATION
# See: https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}
########## END CACHE CONFIGURATION


########## TOOLBAR CONFIGURATION
# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
INSTALLED_APPS += (
    'debug_toolbar',
)

# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
INTERNAL_IPS = ('127.0.0.1',)

# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DEBUG_TOOLBAR_PATCH_SETTINGS = False
# See: https://github.com/django-debug-toolbar/django-debug-toolbar#installation
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TEMPLATE_CONTEXT': True,
    'DEBUG_TOOLBAR_PATCH_SETTINGS': False,
}
########## END TOOLBAR CONFIGURATION

########## STATIC CONFIGURATION
STATIC_URL = '/lims/static/'
STATIC_ROOT = DJANGO_ROOT + "/static"
########## END STATIC CONFIGURATION


########## LDAP CONFIGURATION
logger = logging.getLogger('django_auth_ldap')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# Baseline configuration
AUTH_LDAP_SERVER_URI = "ldap://helicoprion.icm.uu.se:389"
AUTH_LDAP_BIND_DN = ''
AUTH_LDAP_BIND_PASSWORD = ''
AUTH_LDAP_USER_SEARCH = LDAPSearch("ou=people,dc=icm,dc=uu,dc=se", ldap.SCOPE_SUBTREE, "(uid=%(user)s)",)

# Basic group parameters
AUTH_LDAP_GROUP_SEARCH = LDAPSearch("ou=people,dc=icm,dc=uu,dc=se", ldap.SCOPE_SUBTREE)
AUTH_LDAP_GROUP_TYPE = PosixGroupType()

# Simple group restrictions
#AUTH_LDAP_REQUIRE_GROUP = ""
#AUTH_LDAP_DENY_GROUP


# Populate the Django user form the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    "fulllname": "uid",
}

AUTH_LDAP_PROFILE_ATTR_MAP = {
    "fullname": "uid",
}

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    "is_active": "cn=users,ou=group,dc=icm,dc=uu,dc=se",
    "is_staff": "cn=users,ou=group,dc=icm,dc=uu,dc=se",
    "is_superuser": "cn=users,ou=group,dc=icm,dc=uu,dc=se",
}

# This is the default, but I like to be explicit.
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Use LDAP group membership to calculate group permissions
AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

AUTH_LDAP_GLOBAL_OPTIONS = {
    ldap.OPT_X_TLS_REQUIRE_CERT: False,
    ldap.OPT_REFERRALS: False,
}

AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)
AUTH_USER_MODEL = "lims.UserProfile"
########## END LDAP CONFIGURATION
