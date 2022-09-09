"""
Django settings for jaseci project.

Generated by 'django-admin startproject' using Django 3.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "ui/templates")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "@%ad_kyis62uf7qf^w9kv(8$db4)%c$nnnjk^us=s@-gj*)aal"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "knox",
    "django_rest_passwordreset",
    "drf_yasg",
    "jaseci_serv.base",
    "jaseci_serv.user_api",
    "jaseci_serv.obj_api",
    "jaseci_serv.jac_api",
    "corsheaders",
    "django_celery_results",
    "django_celery_beat",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

CORS_ORIGIN_ALLOW_ALL = True

ROOT_URLCONF = "jaseci_serv.jaseci_serv.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [TEMPLATE_DIR],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "jaseci_serv.jaseci_serv.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

if "RDS_HOSTNAME" in os.environ:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": os.environ["RDS_DB_NAME"],
            "USER": os.environ["RDS_USERNAME"],
            "PASSWORD": os.environ["RDS_PASSWORD"],
            "HOST": os.environ["RDS_HOSTNAME"],
            "PORT": os.environ["RDS_PORT"],
        }
    }

elif "POSTGRES_HOST" in os.environ:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": os.environ.get("POSTGRES_HOST"),
            "NAME": os.environ.get("POSTGRES_USER"),
            "USER": os.environ.get("POSTGRES_USER"),
            "PASSWORD": os.environ.get("POSTGRES_PASSWORD"),
            "PORT": os.getenv("POSTGRES_PORT", 5432),
        }
    }

else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "mydatabase",
            "TEST": {"NAME": "test"},
        }
    }

ALLOW_APPS = "test" in sys.argv or "runserver" in sys.argv

# REDIS
REDIS_CONFIG = {
    "enabled": True,
    "host": os.getenv("REDIS_HOST", "localhost"),
    "port": os.getenv("REDIS_PORT", "6379"),
    "db": os.getenv("REDIS_DB", "1"),
}

# TASK_HOOK
TASK_CONFIG = {
    "enabled": True,
    "quiet": False,
    "broker_url": f"redis://{REDIS_CONFIG.get('host')}:{REDIS_CONFIG['port']}/{REDIS_CONFIG['db']}",
    "beat_scheduler": "django_celery_beat.schedulers:DatabaseScheduler",
    "result_backend": "django-db",
    "task_track_started": True,
    "broker_connection_retry_on_startup": True,
}

# EMAIL_HOOK
EMAIL_CONFIG = {
    "enabled": True,
    "version": 1,
    "tls": True,
    "host": "smtp.gmail.com",
    "port": 587,
    "sender": "Jaseci Admin<boyong@jaseci.org>",
    "user": "jaseci.dev@gmail.com",
    "pass": "yrtviyrdzmzdpjxg",
    "backend": "smtp",
    "templates": {
        "activation_subj": "Please activate your account!",
        "activation_body": "Thank you for creating an account!\n\n"
        "Activation Code: {{code}}\n"
        "Please click below to activate:\n{{link}}",
        "activation_html_body": "Thank you for creating an account!<br><br>"
        "Activation Code: {{code}}<br>"
        "Please click below to activate:<br>"
        "{{link}}",
        "resetpass_subj": "Password Reset for Jaseci Account",
        "resetpass_body": "Your Jaseci password reset token is: {{token}}",
        "resetpass_html_body": "Your Jaseci password reset" "token is: {{token}}",
    },
    "migrate": False,
}

if "test" in sys.argv or "test_coverage" in sys.argv:
    EMAIL_CONFIG["backend"] = "locmem"
    TASK_CONFIG["task_always_eager"] = True
    TASK_CONFIG["task_store_eager_result"] = True
    TASK_CONFIG["beat_scheduler"] = "celery.beat:PersistentScheduler"

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        + "UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation." + "MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation." + "CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation." + "NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]

# Sets global default user model to be custom
AUTH_USER_MODEL = "base.User"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 100,
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "knox.auth.TokenAuthentication",
    ],
}

REST_KNOX = {
    "TOKEN_TTL": None,
}

LOGIN_URL = "/ui/login"
LOGIN_REDIRECT_URL = "/ui"
LOGOUT_REDIRECT_URL = "/ui"

# Configs to Manage by Jaseci
JASECI_CONFIGS = [
    "EMAIL_BACKEND",
    "EMAIL_USE_TLS",
    "EMAIL_HOST",
    "EMAIL_HOST_USER",
    "EMAIL_HOST_PASSWORD",
    "EMAIL_PORT",
    "EMAIL_DEFAULT_FROM",
    "EMAIL_ACTIVATION_SUBJ",
    "EMAIL_ACTIVATION_BODY",
    "EMAIL_ACTIVATION_HTML_BODY",
    "EMAIL_RESETPASS_SUBJ",
    "EMAIL_RESETPASS_BODY",
    "EMAIL_RESETPASS_HTML_BODY",
    "LOGIN_TOKEN_TTL_HOURS",
]

DJANGO_CELERY_BEAT_TZ_AWARE = False
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
