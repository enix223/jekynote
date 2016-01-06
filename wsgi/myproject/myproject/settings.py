"""
Django settings for myproject project.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
DJ_PROJECT_DIR = os.path.dirname(__file__)
BASE_DIR = os.path.dirname(DJ_PROJECT_DIR)
WSGI_DIR = os.path.dirname(BASE_DIR)
REPO_DIR = os.path.dirname(WSGI_DIR)
DATA_DIR = os.environ.get('OPENSHIFT_DATA_DIR', BASE_DIR)

import sys
sys.path.append(os.path.join(REPO_DIR, 'libs'))
import secrets
SECRETS = secrets.getter(os.path.join(DATA_DIR, 'secrets.json'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRETS['secret_key']

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG') == 'True'

from socket import gethostname
ALLOWED_HOSTS = [
    gethostname(), # For internal OpenShift load balancer security purposes.
    os.environ.get('OPENSHIFT_APP_DNS'), # Dynamically map to the OpenShift gear name.
    #'example.com', # First DNS alias (set up in the app)
    #'www.example.com', # Second DNS alias (set up in the app)
]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
    'south',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    #'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

# GETTING-STARTED: change 'myproject' to your project name:
ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'myproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            # GETTING-STARTED: change 'db.sqlite3' to your sqlite3 database:
            'NAME': os.path.join(DATA_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'HOST': os.environ.get('OPENSHIFT_MYSQL_DB_HOST'),
            'NAME': os.environ.get('OPENSHIFT_GEAR_NAME'),
            'USER': os.environ.get('OPENSHIFT_MYSQL_DB_USERNAME'),
            'PASSWORD': os.environ.get('OPENSHIFT_MYSQL_DB_PASSWORD'),
            'PORT': os.environ.get('OPENSHIFT_MYSQL_DB_PORT'),
        }
    }

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'

if DEBUG:
    STATIC_ROOT = ''
    STATICFILES_DIRS = (
        os.path.join(WSGI_DIR, 'static'),
    )
else:
    STATIC_ROOT = os.path.join(WSGI_DIR, 'static')


# Web site title
WEBSITE_TITLE = 'Jekynote'
WEBSITE_SOLOGAN = 'Publish your evernotes to jekyll site'

# Login settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/console/'

# Evernote related Constant
EVERNOTE_CUSUMER_KEY = 'enixyu'
EVERNOTE_CUSUMER_SECRET = 'd1a2d1b3f1940d51'
EVERNOTE_DEVELOPER_TOKEN = 'S=s1:U=91a6c:E=1583dbbcf62:C=150e60aa220:P=1cd:A=en-devtoken:V=2:H=becbc7f5f84b6913279853e65381ddef'


# GITHUB related constant
GITHUB_CLIENT_ID = '1c9900220b2ba1c6b123'
GITHUB_CLIENT_SECRET = '4f4e7e81485f8167801615959e7fff87f434d01c'

# Logging settings
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'django.utils.log.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(WSGI_DIR, 'log', 'django.log'),
            'maxBytes': 1024*1024*5,
            'backupCount': 10,
            'formatter': 'verbose',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['null'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.request': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}
