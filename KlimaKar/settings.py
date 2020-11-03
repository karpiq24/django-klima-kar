import os

from django.utils.log import DEFAULT_LOGGING


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ""
SECRET_SALT = ""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

EMAIL_SUBJECT_PREFIX = "[Klima-Kar]"

# Application definition

INSTALLED_APPS = [
    "dal",
    "dal_select2",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django_tables2",
    "django_filters",
    "widget_tweaks",
    "compressor",
    "django_rq",
    "defender",
    "ariadne.contrib.django",
    "KlimaKar",
    "apps.settings",
    "apps.warehouse",
    "apps.invoicing",
    "apps.commission",
    "apps.stats",
    "apps.accounts",
    "apps.audit.apps.AuditConfig",
    "apps.search.apps.SearchConfig",
    "apps.wiki.apps.WikiConfig",
    "apps.mycloudhome.apps.MycloudhomeConfig",
    "apps.employees.apps.EmployeesConfig",
    "tiles.apps.TilesConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "defender.middleware.FailedLoginMiddleware",
    "KlimaKar.middleware.LoginRequiredMiddleware",
]

ROOT_URLCONF = "KlimaKar.urls"
LOGIN_URL = "/konta/zaloguj"
LOGIN_EXEMPT_URLS = ["konta/first_step_login/"]
LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "accounts:login"
TOKEN_VALID_TIME = 600
DEFENDER_ACCESS_ATTEMPT_EXPIRATION = 336
AUDIT_LOG_EXPIRATION = 336
TWO_STEP_LOGIN_ENABLED = True

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "KlimaKar.context_processors.issue_form",
                "KlimaKar.context_processors.debug",
            ],
        },
    },
]

WSGI_APPLICATION = "KlimaKar.wsgi.application"


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}


# Cache

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient",},
    }
}

CACHE_FILE_TIMEOUT = None


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = "pl-pl"

TIME_ZONE = "Europe/Warsaw"

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = "/static/"

STATICFILES_DIRS = (os.path.join(BASE_DIR, "KlimaKar/static/"),)

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
)

COMPRESS_FILTERS = {
    "css": [
        "compressor.filters.css_default.CssAbsoluteFilter",
        "compressor.filters.cssmin.rCSSMinFilter",
    ],
    "js": ["compressor.filters.jsmin.JSMinFilter"],
}

COMPRESS_OUTPUT_DIR = "compressed"

DJANGO_TABLES2_TEMPLATE = "tables2/table.html"

TEMPORARY_UPLOAD_DIRECTORY = os.path.join(BASE_DIR, "temp")
HOURS_TO_REMOVE_STALE_FILES = 2

RQ_QUEUES = {"default": {"HOST": "localhost", "PORT": 6379, "DB": 0,}}

# Logging
DEFAULT_LOGGING["loggers"]["rq.worker"] = {
    "handlers": ["console", "mail_admins"],
    "level": "INFO",
}
DEFAULT_LOGGING["loggers"]["commands"] = {
    "handlers": ["mail_admins"],
    "level": "ERROR",
    "propagate": True,
}

# GEOIP2
GEOIP_PATH = "data/"
GEOIP_COUNTRY = "GeoLite2-Country.mmdb"


# VAT
UE_VALIDATE_VAT = "http://ec.europa.eu/taxation_customs/vies/checkVatService.wsdl"
UE_VIEW_VAT = "http://ec.europa.eu/taxation_customs/vies/?locale=pl"
PL_VALIDATE_VAT = "https://wl-api.mf.gov.pl/api/search/nip/{}?date={}"
PL_VIEW_VAT = "https://www.podatki.gov.pl/wykaz-podatnikow-vat-wyszukiwarka"


def FILTERS_VERBOSE_LOOKUPS():
    from django_filters.conf import DEFAULTS

    verbose_lookups = DEFAULTS["VERBOSE_LOOKUPS"].copy()
    verbose_lookups.update({"icontains": ""})
    return verbose_lookups


try:
    from KlimaKar.settings_local import *  # noqa
except ImportError:
    pass
