import os

import redis

# DaRkHaWk72

RIOT_API_KEY = 'RGAPI-0f0cd528-9c25-4494-bc33-2e16af5a385f'

APP_DOMAIN = 'localhost:8000'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ALLOWED_HOSTS = ['*']

CORS_ORIGIN_ALLOW_ALL = True

HEARTBEAT_RATE = int(os.environ['HEARTBEAT_RATE'])

# List of administrators
ADMINS = (
    ('Max Halford', 'maxhalford25@gmail.com'),
)

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_rq',

    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
]

ROOT_URLCONF = 'core.urls'

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

WSGI_APPLICATION = 'lolmd.wsgi.application'

# Database configuration
# https://docs.djangoproject.com/en/2.1/ref/databases/
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, f'{os.environ["DB_NAME"]}.sqlite3'),
    }
}

# Redis connection pool
REDIS_POOL = redis.ConnectionPool(
    host=os.environ['REDIS_HOST'],
    port=os.environ['REDIS_PORT'],
    db=os.environ['REDIS_DB'],
    password=os.environ['REDIS_PASSWORD'],
    decode_responses=True
)

# rq config
# https://github.com/rq/django-rq

RQ_QUEUES = {
    'default': {
        'HOST': os.environ['REDIS_HOST'],
        'PORT': os.environ['REDIS_PORT'],
        'DB': os.environ['REDIS_DB'],
        'PASSWORD': os.environ['REDIS_PASSWORD'],
        'DEFAULT_TIMEOUT': 360,
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
STATIC_URL = '/static/'

# Media files (user uploads)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'
