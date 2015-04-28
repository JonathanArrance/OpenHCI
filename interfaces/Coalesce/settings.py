#!/usr/local/bin/python2.7
# Django settings for transcirrus project.
import os.path
import sys
import coalesce

PROJECT_PATH = os.path.abspath(os.path.dirname(__name__))
ROOT_PATH = os.path.dirname(__file__).replace('\\','/')
ALLOWED_HOSTS = ['*']

# Set the path to the packages in /src
SRC_PATH =  os.path.join(PROJECT_PATH, 'src')
if SRC_PATH not in sys.path:
    sys.path.insert(1, SRC_PATH)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': '/opt/Coalesce/tc',
    }
}


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = ''

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Tell Django auth about the new user profile, UserProfile, so that we can
# do checks on customer.
AUTH_PROFILE_MODULE = 'coal_beta.UserProfile'



# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'csvfiles')


# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/upload_images/'



# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '%#tl*x)mf1t@mss2rlyo2^@_v+eu$2k!g9$h7sh*!a6fm$to3!'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',

#	'django.template.loaders.filesystem.load_template_source',
#	'django.template.loaders.app_directories.load_template_source',
#	'django.template.loaders.filesystem.Loader',
#	'django.template.loaders.app_directories.Loader',

)


MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'urls'


TEMPLATE_DIRS = (
    os.path.join(ROOT_PATH, 'templates'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

STATIC_ROOT = ''
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(PROJECT_PATH, 'static'),)
CRISPY_TEMPLATE_PACK = 'bootstrap'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'django.contrib.staticfiles',
    'bootstrap_toolkit',
    'django_tables2',
    'django_filters',
    'crispy_forms',
    'coalesce.coal_beta',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'coalesce.coal_beta.context_processors.global_vars',

)

FILE_UPLOAD_HANDLERS = (
    "coalesce.coal_beta.UploadProgressCachedHandler.UploadProgressCachedHandler",   # we must have our handler listed first because
    "django.core.files.uploadhandler.MemoryFileUploadHandler",                      # the handlers are called in order of being listed;
    "django.core.files.uploadhandler.TemporaryFileUploadHandler",)                  # otherwise not all of our functions will be called.

LOGIN_REDIRECT_URL = '/'

LOGIN_URL = '/coal/login_page/'

CSRF_COOKIE_AGE = None

SESSION_EXPIRE_AT_BROWSER_CLOSE = False

SESSION_COOKIE_AGE = 3600

SESSION_SAVE_EVERY_REQUEST = True

CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
