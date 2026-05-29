import datetime
import importlib.metadata
import json
import os, os.path
import warnings
# from urllib.parse import cast

from pathlib import Path


import dj_database_url
import dj_email_url
# import django_cache_url
from django.core.exceptions import ImproperlyConfigured
from django.core.validators  import URLValidator


from api.languages import LANGUAGES as CORE_LANGUAGES


def get_list(text):
    return [item.strip() for item in text.split(",") if item]


def get_bool_from_env(name, def_value):
    """
    Retrieve and convert an environment variable to a boolean object.

    Accepted values are `true` (case-insensitive) and `1`, any other value resolves to `False`.
    """

    value = os.environ.get(name)
    if value is None:
        return def_value
    return value.lower() in ("true", "1")


def get_url_from_env(name, *, schemes=None)-> str | None:
    if name in os.environ:
        value = os.environ['name']
        msg = f'{value} is an invalid value for {name}'
        URLValidator(schemes=schemes, message=msg)(value)
        return value
    return None

DEBUG = get_bool_from_env("DEBUG", True)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

ADMINS = ("Muzi Dube", "muzingaye.dube@gmail.com")

APPEND_SLASH = False
_DEFAULT_CLIENT_HOSTS = "localhost, 127.0.0.1"

ALLOWED_CLIENT_HOSTS = os.environ.get("ALLOWED_CLIENT_HOSTS")
if not ALLOWED_CLIENT_HOSTS:
    if DEBUG: 
        ALLOWED_CLIENT_HOSTS = _DEFAULT_CLIENT_HOSTS
    else:
        raise ImproperlyConfigured(
            'ALLOWED_CLIENT_HOSTS environment variable must be set when DEBUG=False.'
        )


ALLOWED_CLIENT_HOSTS = get_list(ALLOWED_CLIENT_HOSTS)


INTERNAL_IPS = get_list(os.environ.get("INTERNAL_IPS", "127.0.0.1"))

DB_CONN_MAX_AGE = int(os.environ.get("DB_CONN_MAX_AGE", 0))


DATABASE_CONNECTION_DEFAULT_NAME = 'default'

DATABASE_CONNECTION_REPLICA_NAME = "replica"

SECRET_KEY = 'django-insecure-rhu#0d&pdtux^eusr1+vt1@!)+ajdz57du4p39-&g7b78*io(@'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS =    [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # local apps
    "permission",
    # "auth",
    "account",
    "core",
    "api",

]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'demo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'demo.wsgi.application'

# Database


if "DATABASE_URL_REPLICA" in os.environ:
    DATABASE_URL_REPLICA_ENV_NAME = "DATABASE_URL_REPLICA"
else:
    DATABASE_URL_REPLICA_ENV_NAME =  dj_database_url.DEFAULT_ENV

DATABASES = {
    DATABASE_CONNECTION_DEFAULT_NAME: dj_database_url.config(
        env=dj_database_url.DEFAULT_ENV,
        default="mssql://localhost/DjangoDemo?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes",
        engine="mssql",
        conn_max_age=DB_CONN_MAX_AGE,
    ),
    DATABASE_CONNECTION_REPLICA_NAME: dj_database_url.config(
        env=DATABASE_URL_REPLICA_ENV_NAME,
        default="mssql://localhost/DjangoDemo?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes",
        engine="mssql",
        conn_max_age=DB_CONN_MAX_AGE,
        test_options={"MIRROR": DATABASE_CONNECTION_DEFAULT_NAME},
    ),
}

DATABASE_ROUTERS = ["api.db_routers.PrimaryReplicaRouter"]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
LANGUAGES: list[tuple[str,str]]= CORE_LANGUAGES
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
