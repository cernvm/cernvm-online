#
# CernVM Online Configuration file
# Modify the config.py file for the current deployment
#
import os
from cvmo import config

#
# General
#

SITE_ID = 1
ROOT_URLCONF = "cvmo.urls"
WSGI_APPLICATION = "cvmo.wsgi.application"
DEBUG = config.DEBUG
ADMINS = config.ADMINS
MANAGERS = config.ADMINS
ALLOWED_HOSTS = config.ALLOWED_HOSTS
SECRET_KEY = config.SECRET_KEY
URL_PREFIX = config.URL_PREFIX

#
# CSC
#

ENABLE_CSC = False
CSC_USER_CONFIG_FILE = "students.conf"

#
# Cloud
#

ENABLE_CLOUD = config.ENABLE_CLOUD

#
# WebAPI
#

WEBAPI_UCERNVM_VERSION = config.WEBAPI_UCERNVM_VERSION
WEBAPI_CONFIGURATIONS = config.WEBAPI_CONFIGURATIONS


#
# User registration
#

GOOGLE_RECAPTCHA = config.GOOGLE_RECAPTCHA
ACTIVATION_EMAIL = config.ACTIVATION_EMAIL

#
# Cookies
#

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 3600
SESSION_COOKIE_PATH = "/" + config.URL_PREFIX
CSRF_COOKIE_PATH = "/" + config.URL_PREFIX


#
# Shibboleth plugin
#

SHIBBOLETH_SSO = {
    # Header bindings
    "login_header": "HTTP_ADFS_LOGIN",
    "groups_header": "HTTP_ADFS_GROUP",
    "fullname_header": "HTTP_ADFS_FULLNAME",
    "email_header": "HTTP_ADFS_EMAIL",

    # Groups to add to the user, depending on groups_header
    "map_groups": {
        "admin": r"(;|^)cernvm-infrastructure(;|$)"
    },

    # Which regex on groups_header should mark the user as staff
    "staff_groups": [
        r"(;|^)cernvm-infrastructure(;|$)"
    ],

    # Where to redirect if the user is not authenticated
    "redirect_login": "/%suser/login" % config.URL_PREFIX,

    # Which website paths are publicly accessible
    "public_path": [
        # Admin
        r"/%sadmin[/]{0,1}.*$" % config.URL_PREFIX,
        # Login
        r"/%suser/login$" % config.URL_PREFIX,
        r"/%suser/login_action$" % config.URL_PREFIX,
        # Registration
        r"/%suser/register$" % config.URL_PREFIX,
        r"/%suser/register_action$" % config.URL_PREFIX,
        r"/%suser/account_activation$" % config.URL_PREFIX,
        # API
        r"/%sapi/.*$" % config.URL_PREFIX

        # API - context
        # r"/" + config.URL_PREFIX + "api/context/?$",
        # r"/" + config.URL_PREFIX + "api/context/[0-9a-f]+/?$",
        # r"/" + config.URL_PREFIX + "api/context/[0-9a-f]+/plain/?$",
        # r"/" + config.URL_PREFIX + "api/fetch/?$",
    ]
}

#
# Contextualization plugins
#

CONTEXT_PLUGINS = (
    "cvmo.core.plugin.condor.Condor",
    "cvmo.core.plugin.hostname.Hostname",
    "cvmo.context.plugin.vafsetup.VAFSetup",
    "cvmo.core.plugin.noip.NoIP",
    "cvmo.core.plugin.storage.Storage",
    "cvmo.core.plugin.openvpn.OpenVPN",
    "cvmo.core.plugin.ganglia.Ganglia",
    "cvmo.core.plugin.puppet.Puppet",
)

#
# Django applications
#

INSTALLED_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Admin
    "django.contrib.admin",
    # CernVM-Online
    "cvmo.core",
    # CernVM-Online user
    "cvmo.user",
    # CernVM-Online dashboard
    "cvmo.dashboard",
    # CernVM-Online context
    "cvmo.context",
    # CernVM-Online cluster
    "cvmo.cluster",
    # CernVM-Online market
    "cvmo.market"
)

#
# Django middlewares
#

MIDDLEWARE_CLASSES = (
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    # Shibboleth SSO
    "cvmo.core.middleware.shibsync.ShibbolethUserSync",
    # CORS fix
    "corsheaders.middleware.CorsMiddleware"
)

# Time and language
TIME_ZONE = "Europe/Zurich"
LANGUAGE_CODE = "en-us"
USE_I18N = True
USE_L10N = True
USE_TZ = True

#
# Database
#

DATABASES = {
    "default": {
        "ENGINE":   "django.db.backends." + config.DB.get("backend", "mysql"),
        "HOST":     config.DB.get("host", "localhost"),
        "USER":     config.DB.get("user", "root"),
        "PASSWORD": config.DB.get("password", ""),
        "NAME":     config.DB.get("name", "cvmo"),
        "PORT":     config.DB.get("port", 3306)
    }
}

#
# Logging
#

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "formatters": {
        "verbose": {
            "format": "[%(asctime)s] %(levelname)s %(module)s %(message)s"
        },
        "simple": {
            "format": "%(levelname)s %(message)s"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler"
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose"
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": os.path.join(config.LOG_PATH, "django.log"),
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins", "file"],
            "level": "INFO",
            "propagate": True,
        },
        "cvmo": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        }
    }
}

#
# Media and static
#

MEDIA_ROOT = config.PUBLIC_PATH + "/media/"
MEDIA_URL = "/" + config.URL_PREFIX + "media/"
STATIC_ROOT = config.PUBLIC_PATH + "/static/"
STATIC_URL = "/" + config.URL_PREFIX + "static/"
STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

#
# Templates
#

TEMPLATE_DEBUG = config.DEBUG
TEMPLATE_DIRS = ()
TEMPLATE_LOADERS = (
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "cvmo.core.utils.views.global_context"
)

#
# CORS Configuration
#

CORS_ORIGIN_REGEX_WHITELIST = config.CORS_ORIGIN_REGEX_WHITELIST
