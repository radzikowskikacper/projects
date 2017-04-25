import os
import sys

# PATH vars

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
root = lambda *x: os.path.join(BASE_DIR, *x)

sys.path.insert(0, root('apps'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'r)us38(zp5$kukueshb_3u^_12nf3o4_a9a(odtmezs!bmm#8q'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
IN_TESTING = sys.argv[1:2] == ['test']

ALLOWED_HOSTS = []

# See: https://docs.djangoproject.com/en/1.10/ref/settings/#internal-ips
INTERNAL_IPS = (
    '0.0.0.0',
    '127.0.0.1',
)

# Username of user with access to the admin page.
ADMIN_LOGIN = ''

# Application definition

INSTALLED_APPS = [
    'django_coverage',
    'bootstrap3',
    'projects_helper.apps.common',
    'projects_helper.apps.students',
    'projects_helper.apps.lecturers',
    'projects_helper.apps.about',
    # 'registration',
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
    'projects_helper.settings.middleware.LoggingMiddleware',
    'projects_helper.settings.middleware.StandardExceptionMiddleware',
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
        'NAME': '',
        'USER': '',
        'PASSWORD': '',
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



# Internationalization and localization

from django.utils.translation import ugettext_lazy as _
LANGUAGES = (
    ('en', _('English')),
    ('pl', _('Polski')),
)

LANGUAGE_CODE = 'pl'

TIME_ZONE = 'Poland'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)


# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'

STATICFILES_DIRS = (
    root('static'),
)

STATIC_ROOT = root('staticfiles')

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

# CAS settings. See: https://github.com/mingchen/django-cas-ng

CAS_SERVER_URL = ''
CAS_VERSION = '3'
CAS_LOGOUT_COMPLETELY = True
CAS_IGNORE_REFERER = False
CAS_RETRY_LOGIN = True
CAS_LOGIN_MSG = None
CAS_LOGGED_MSG = None
#CAS_ADMIN_PREFIX = '/admin'
#CAS_REDIRECT_URL = '/common/select_course/'

# Login page
LOGIN_URL = '/login/'
# Logout page
LOGOUT_URL = '/logout/'

# importing test settings file if necessary
if IN_TESTING:
    from .testing import *  # noqa

# Logging settings

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'main_log': {
            'format': '%(asctime)s %(levelname)s %(name)s [%(lineno)s] - %(message)s'
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'filters': ['require_debug_true'],

        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': root('requests.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 5,
        },
        'main_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': root('projects_helper.log'),
            'maxBytes': 1024 * 1024 * 5,  # 5MB
            'backupCount': 5,
            'formatter': 'main_log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'projects_helper': {
            'handlers': ['main_handler'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
