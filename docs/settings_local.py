# -*- coding: utf-8 -*-
import os

# A boolean that turns on/off debug mode.
DEBUG = False
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A list of all the people who get code error notifications.
# When DEBUG=False and a view raises an exception, Django will email these
# people with the full exception information. Each item in the list should be
# a tuple of (Full name, email address).
# Example: [('John', 'john@example.com'), ('Mary', 'mary@example.com')]
ADMINS = []

EMAIL_HOST = ''
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# A list of strings representing the host/domain names that this Django
# site can serve. Values in this list can be fully qualified names.
# A value beginning with a period can be used as a subdomain wildcard.
ALLOWED_HOSTS = ['*']

# The absolute path to the directory
# where collectstatic will collect static files for deployment
STATIC_ROOT = '/var/www/wsgi/static/KlimaKar'

# SECRET_KEY should be unique, unpredictable value.
# Example command to generate secret key in bash:
# tr -dc A-Za-z0-9 < /dev/urandom | head -c 50 | xargs
SECRET_KEY = ''

AUTH_PASSWORD_VALIDATORS = []

# Inter Cars API
IC_API_URL = 'https://katalog.intercars.com.pl/api/v2/External/'
IC_TOKEN = ''
IC_CLIENT_NUMBER = ''
