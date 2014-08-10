# Django settings for ancfindersite project.

import sys
sys.path.append("lib")

import os.path

RECAPTCHA_PUBLIC_KEY = '6LeYAO8SAAAAALEZqtnk4qm7hoh8Iwv_h4lZ3lSe'
RECAPTCHA_PRIVATE_KEY = '6LeYAO8SAAAAAICslEpPIpmMmkFiuNs_hrAzSRxx'

environment_file = '/home/ancfinder/environment.yaml'

if not os.path.exists(environment_file):
	# Settings for local (not public) deployments.

	print "Running a local deployment..."

	DEBUG = True
	TEMPLATE_DEBUG = DEBUG

	# For a simple setup when debugging, we'll hard-code these values.
	SECRET_KEY = '7^^6oohvb%oc3$&amp;4z^#vplkp(!@dy24nm$d6a2g9^w#imqpme8'

	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.sqlite3',
			'NAME': os.path.join(os.path.dirname(__file__), 'database.sqlite').replace('\\','/'),
		}
	}

	EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

	ADMINS = (
		# ('Your Name', 'your_email@example.com'),
	)
	
	MANAGERS = ADMINS
	
	ALLOWED_HOSTS = ["*"]

	# Absolute path to the directory static files should be collected to.
	# Don't put anything in this directory yourself; store your static files
	# in apps' "static/" subdirectories and in STATICFILES_DIRS.
	# Example: "/home/media/media.lawrence.com/static/"
	STATIC_ROOT = os.path.join(os.path.dirname(__file__), '../static') + '/'

else:
	# Settings for a public deployment.
	
	DEBUG = False
	TEMPLATE_DEBUG = False

	import yaml
	with open(environment_file) as f:
	  env = yaml.load(f)
	SECRET_KEY = env['DJANGO_SECRET_KEY']
	DATABASES = {
		'default': {
			'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': env['DATABASE_HOST'],
            'PORT': int(env['DATABASE_PORT']),
			'NAME': env['DATABASE_NAME'],
			'USER': env['DATABASE_USERNAME'],
			'PASSWORD': env['DATABASE_PASSWORD'],
		}
	}

	ADMINS = env['ADMINS']
	MANAGERS = ADMINS

	EMAIL_HOST = env['SMTP_HOST']
	EMAIL_HOST_USER = env['SMTP_USER']
	EMAIL_HOST_PASSWORD = env['SMTP_PASSWORD']
	EMAIL_USE_TLS = True

	ALLOWED_HOSTS = ["*"] # anything unexpected will be filtered out by the http server

	OPENID_TEMP_FOLDER = "/tmp/openid-ancfinder"

	# Absolute path to the directory static files should be collected to.
	# Don't put anything in this directory yourself; store your static files
	# in apps' "static/" subdirectories and in STATICFILES_DIRS.
	# Example: "/home/media/media.lawrence.com/static/"
	STATIC_ROOT = env["STATIC_ROOT"]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/New_York'

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

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (os.path.join(os.path.dirname(__file__), 'static'),
    #'/static/',
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

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
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'ancfindersite.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'ancfindersite.wsgi.application'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/'),
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    'django.core.context_processors.request',
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    'ancfindersite.views.TemplateContextProcessor',
    )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',
    
    'bootstrapform',
    'tinymce',

    'registration',
    'emailverification',
    
    'ancfindersite',
    'annotator',
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
APP_NICE_SHORT_NAME = "ANCFinder.org"
SERVER_EMAIL = "ANCFinder.org <no.reply@ancfinder.org>" # From: address on verification emails
REGISTRATION_ASK_USERNAME = True
SITE_ROOT_URL = "http://www.ancfinder.org"
