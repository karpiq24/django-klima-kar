import os

# A boolean that turns on/off debug mode.
DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# A list of all the people who get code error notifications.
# When DEBUG=False and a view raises an exception, Django will email these
# people with the full exception information. Each item in the list should be
# a tuple of (Full name, email address).
# Example: [('John', 'john@example.com'), ('Mary', 'mary@example.com')]
ADMINS = [("Bartosz", "karpiq@gmail.com")]
MANAGERS = [("Bartosz", "karpiq@gmail.com")]

EMAIL_HOST = ""
EMAIL_HOST_USER = ""
EMAIL_HOST_PASSWORD = ""
EMAIL_PORT = 465
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
DEFAULT_FROM_EMAIL = ""

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": "klimakar",
        "USER": "user",
        "PASSWORD": "password",
        "HOST": "localhost",
        "PORT": "",
    }
}

# A list of strings representing the host/domain names that this Django
# site can serve. Values in this list can be fully qualified names.
# A value beginning with a period can be used as a subdomain wildcard.
ALLOWED_HOSTS = ["*"]

# The absolute path to the directory
# where collectstatic will collect static files for deployment
STATIC_ROOT = "/home/bartosz/KlimaKar/static/"

# SECRET_KEY should be unique, unpredictable value.
# Example command to generate secret key in bash:
# tr -dc A-Za-z0-9 < /dev/urandom | head -c 50 | xargs
SECRET_KEY = "fgpoh6546%$@#GHgfhd4DHcx6"

AUTH_PASSWORD_VALIDATORS = []

# Inter Cars API
IC_API_URL = "https://katalog.intercars.com.pl/api/v2/External/"

# Dropbox
DROPBOX_TOKEN = ""

# GUS API KEY
GUS_SANDBOX = False
GUS_KEY = ""

# GitHub
GITHUB_USERNAME = ""
GITHUB_TOKEN = ""
GITHUB_REPOSITORY = "karpiq24/django-klima-kar"

# Ware price changes alerts
PRICE_CHHANGE_PERCENTAGE = 5

# Reports settings
ABSOLUTE_URL = ""
REPORT_EMAILS = []
REPORT_PRICE_CHANGE_PERCENTAGE = {"week": 5, "month": 10, "year": 25}

# SMSAPI
SMSAPI_TOKEN = ""
SMSAPI_LOW_BALANCE_COUNT = 20

COMPRESS_ENABLED = False

# WD MyCloud Home
WD_REDIRECT_URL = ""
WD_DELETE_FILES = False

# Ekosystem
EKOSYSTEM_NUMBER = ""
EKOSYSTEM_ENDPOINT = ""
