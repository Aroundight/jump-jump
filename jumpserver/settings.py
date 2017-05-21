"""
Django settings for jumpserver project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import getpass

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
KEY_DIR = os.path.join(BASE_DIR, 'keys')

#AUTH_USER_MODEL = 'juser.User'
# mail config
MAIL_ENABLE = True
EMAIL_HOST = "smtp.qiye.163.com"
EMAIL_PORT = 465
EMAIL_HOST_USER = "test@oxx.so"
EMAIL_HOST_PASSWORD = "test"
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False
EMAIL_BACKEND = 'django_smtp_ssl.SSLEmailBackend' if EMAIL_USE_SSL else 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_TIMEOUT = 5

# ======== Log ==========
LOG_DIR = os.path.join(BASE_DIR, 'logs')
SSH_KEY_DIR = os.path.join(BASE_DIR, 'keys/role_keys')
KEY = '941enj9neshd1wes'
URL = 'http://127.0.0.1'
LOG_LEVEL = 'debug'
IP = '0.0.0.0'
PORT = '8000'


NAV_SORT_BY = 'ip'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '!%=t81uof5rhmtpi&(zr=q^fah#$enny-c@mswz49l42j0o49-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0/8']

AUTHENTICATION_BACKENDS = (  
    'ops_auth.auth.OpsAuthBackend',
)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django_crontab',
    'bootstrapform',
    'jumpserver',
    'juser',
    'jasset',
    'jperm',
    'jlog',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'jumpserver.urls'

WSGI_APPLICATION = 'jumpserver.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': "jump",
        'USER': "jump",
        'PASSWORD': "jump",
        'HOST': "192.168.1.1",
        'PORT': "3306",
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'jumpserver.context_processors.name_proc',
)

TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'templates'),
)

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "static"),
)
# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'zh_CN'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

IME_ZONE = 'Asia/Shanghai'

USE_TZ = False


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'

BOOTSTRAP_COLUMN_COUNT = 10

CRONJOBS = [
    #('0 1 * * *', 'jasset.asset_api.asset_ansible_update_all'),
    ('*/10 * * * *', 'jlog.log_api.kill_invalid_connection'),
]

DATE_FORMAT = '%m-%d-%y %H:%M:%S'

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
        },
        'console': {  
            'level': 'DEBUG',  
            'class':'logging.StreamHandler' 
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        '': {
            'handlers': ['console'],
            'propagate': True,
            'level':'INFO',
        },
        'root': {
            'handlers': ['console'],
            'propagate': True,
            'level':'INFO',
        },         
    },
}

OPS_KEY = "IfdED2Y3"
OPS_USER_INFO_URL = "http://192.168.1.1:2053/jump/api/getUserInfo/"
OPS_USER_AUTH_URL = "http://192.168.1.1:2053/jump/api/jumpUserAuth/"
OPS_USER_GROUP_URL = "http://192.168.1.1:2053/jump/api/getUserItem/"
OPS_HOST_IN_GROUP_URL = "http://192.168.1.1:2053/jump/api/getUserPermissions/"
