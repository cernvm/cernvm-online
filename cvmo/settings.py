# Django settings for cvmo project.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ( 'CernVM', 'admin@cernvm.com' )
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',         # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/var/www/html/db.sqlite3',             # Or path to database file if using sqlite3.
        'USER': '',                                     # Not used with sqlite3.
        'PASSWORD': '',                                 # Not used with sqlite3.
        'HOST': '',                                     # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                                     # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'UTC'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ( 'static', '/var/www/html/cvmo/static' )
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '^p+u-t6^*gtqmj85l$prq(q33#7i+(#$5o0*t0pvm4@1-t_a^w'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'cvmo.context.middleware.shibsync.ShibbolethUserSync'
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'cvmo.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'cvmo.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/var/www/html/cvmo/templates'
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
    
    # CernVM Contextualization
    'cvmo.context',
    
    # CernVM Online Wiki
    "cvmo.wiki"
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages",
    "cvmo.context.utils.views.global_context" 
)

CONTEXT_PLUGINS = (
    'cvmo.context.plugin.noip.NoIP',
    'cvmo.context.plugin.storage.Storage',
    'cvmo.context.plugin.hostname.Hostname',
    'cvmo.context.plugin.condor.Condor'
)

SHIBBOLETH_SSO = {

    # Header bindings
    'login_header': 'HTTP_ADFS_LOGIN',
    'groups_header': 'HTTP_ADFS_GROUP',
    'fullname_header': 'HTTP_ADFS_FULLNAME',
    'email_header': 'HTTP_ADFS_EMAIL',
    
    # Groups to add to the user, depending on groups_header
    'map_groups': {
        'admin': r'(;|^)cernvm-infrastructure(;|$)'
    },
    
    # Which regex on groups_header should mark the user as staff
    'staff_groups': [
        r'(;|^)cernvm-infrastructure(;|$)'
    ],
    
    # Where to redirect if the user is not authenticated
    'redirect_login': '/login',
    
    # Which website paths are publicly accessible
    'public_path': [
        r'/login$',
        r'/login_action$',
        r'/register$',
        r'/register_action$',
        r'/account_activation$',
        r'/api/fetch/?$',
        r'/api/cluster/.*$'#,
#        r'/wiki/.*$'
#        r'/csc$',
#        r'/csc/do_login$',
    ]
}

# 1 hour of session 
SESSION_COOKIE_AGE = 3600

# Expire session at browser close
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Weather to enable or disable the cloud
ENABLE_CLOUD = True

# Whether to enable or disable the CSC UI
ENABLE_CSC = False

# Recaptcha information for the user registration
GOOGLE_RECAPTCHA = {
    # cernvm-online.cern.ch keys
#    "public_key": "6LdG6tMSAAAAAMDBse8Dzze0Wz_3WGTwfUdyz60Z",
#    "private_key": "6LdG6tMSAAAAAJTx1HqU69b-r90tERI51U8Gn-F2"
    # localhost keys
    "public_key": "6Lf-6tMSAAAAAINhybwn_uxxdugd9nfDv5NCx-tY",
    "private_key": "6Lf-6tMSAAAAAIAMH0F6OLvySp--S6aPWoQGW_bU"    
}

# Where to send activation mail
ACTIVATION_EMAIL = {
    "sender": "CernVM Online",
    "sender_email": "info@cernvm-online.cern.ch",
    "subject": "Account activation"
}
