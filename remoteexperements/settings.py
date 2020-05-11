"""
Django settings for remoteexperements project.

Generated by 'django-admin startproject' using Django 3.0.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os
# import djcelery

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'eo1plcz2%!%2+c&g#5kq(abs+u8dk!sre!!zs3*!y1vfw%#ml!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.0.106', '127.0.0.1']

# djcelery.setup_loader()

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'auth_and_static.apps.TaskshowerConfig',
    'task_controller.apps.TaskControllerConfig'
    # 'djcelery',
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

ROOT_URLCONF = 'remoteexperements.urls'

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

WSGI_APPLICATION = 'remoteexperements.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

env = os.environ.copy()
if 'GAC_DB_LOCALHOST' in env:
    db_host = env['GAC_DB_LOCALHOST']
else:
    db_host = 'localhost'
if 'GAC_QUEUE_LOCALHOST' in env:
    queue_host = env['GAC_QUEUE_LOCALHOST']
else:
    queue_host = 'localhost'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'sqlite3.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
# for postgres
##############################################################################################################
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': 'postgres',
#         'USER': 'postgres',
#         'PASSWORD': 'postgres',
#         'HOST': db_host,
#         'PORT': '5432',
#     }
# }
###########################################################################################################3

CELERY_BROKER_HOST = queue_host
CELERY_BROKER_PORT = 5672
CELERY_BROKER_USER = "guest"
CELERY_BROKER_PASSWORD = "guest"
CELERY_BROKER_VHOST = "my_vhost"


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR,"static_files")
STATIC_URL = '/static/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)


MEDIA_ROOT = BASE_DIR + '/data/'

APPEND_SLASH = False

USED_TASKS = [
    'task_controller.tasks.HelloWorld',
    'task_controller.tasks.HelloWorld2',
]
