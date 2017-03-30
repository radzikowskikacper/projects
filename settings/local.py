"""Machine specific settings."""

from .base import *
try:
	import config_custom
except Exception as e:
    print ('[Exception] File config_custom.py not found. Copy content of config_default.py, '
        'change parameters to custom values and run configure.py again.')
    print('('+ str(e) +')')
    exit()



DEBUG = True

ALLOWED_HOSTS += ('127.0.0.1','localhost', config_custom.ALLOWED_HOST)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': config_custom.DB_NAME,
        'USER': config_custom.DB_USER,
        'PASSWORD': config_custom.DB_PASSWORD,
        'HOST': config_custom.DB_HOST,
        'PORT': '5432',
    }
}

ADMIN_LOGIN = config_custom.ADMIN_LOGIN

CAS_SERVER_URL = config_custom.CAS_URL
