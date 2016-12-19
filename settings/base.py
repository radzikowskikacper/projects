import os
import sys

# PATH vars

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root = lambda *x: os.path.join(BASE_DIR, *x)

sys.path.insert(0, root('apps'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'CHANGE THIS!!!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
IN_TESTING = sys.argv[1:2] == ['test']

ALLOWED_HOSTS = []

# Insert username of the superuser/admin below
ADMIN_LOGIN = ''

# Application definition

INSTALLED_APPS = [
    'django_coverage',
    'bootstrap3',
    'projects_helper.apps.common',
    'projects_helper.apps.students',
    'projects_helper.apps.lecturers',
    'registration',
    'django.contrib.admin.apps.SimpleAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cas_ng'
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    #'django_cas_ng.backends.CASBackend',
    'common.backends.ExtendedCASBackend'
)


ROOT_URLCONF = 'projects_helper.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'projects_helper.wsgi.application'

# Database

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'projects_helper',
        'USER': 'projects_user',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '',
    }
}

if IN_TESTING:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': '/tmp/projects_helper_test.db',
        }
    }

# Internationalization

from django.utils.translation import ugettext_lazy as _
LANGUAGES = (
    ('en', _('English')),
    ('pl', _('Polski')),
)

LANGUAGE_CODE = 'pl'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

# Additional locations of static files

STATICFILES_DIRS = (
    root('assets'),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'APP_DIRS': True,
        'DIRS': [
            root('templates'),
        ],
        'OPTIONS': {
            'debug': DEBUG,
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    }
]

# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# CAS
CAS_SERVER_URL = 'https://merkury.elka.pw.edu.pl/cas/'
CAS_ADMIN_PREFIX = '/admin'
CAS_VERSION = '3'
CAS_LOGOUT_COMPLETELY = True
CAS_IGNORE_REFERER = False
CAS_RETRY_LOGIN = True
CAS_LOGIN_MSG = None
CAS_LOGGED_MSG = None
#CAS_REDIRECT_URL = '/common/select_course/'

# Login page
LOGIN_URL = '/login/'
# Logout page
LOGOUT_URL = '/logout/'

# User model
AUTH_USER_MODEL = 'common.CustomUser'

# .local.py overrides all the common settings.
try:
    from .local import *  # noqa
except ImportError:
    pass

# importing test settings file if necessary
if IN_TESTING:
    from .testing import *  # noqa
