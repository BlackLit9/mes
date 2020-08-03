"""
Django settings for mes project.

Generated by 'django-admin startproject' using Django 2.2.14.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os, datetime

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.utils.translation import ugettext_lazy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '@(e8hu481p171x)jz!40a$@gt6@_=#2_g-sscjrc531tsxz0(d'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = eval(os.environ.get('DEBUG', 'True'))

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',  # swgger文档插件    /api/v1/docs/swagger
    'django_filters',
    'production.apps.ProductionConfig',
    'plan.apps.PlanConfig',
    'basics.apps.BasicsConfig',
    'system.apps.SystemConfig',
    'recipe.apps.RecipeConfig',
    'gui.apps.GuiConfig',
    'docs.apps.DocsConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'mes.middlewares.DisableCSRF',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mes.urls'
AUTH_USER_MODEL = 'system.User'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

WSGI_APPLICATION = 'mes.wsgi.application'

# drf通用配置
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',  # 文档
    'DEFAULT_PERMISSION_CLASS': ('rest_framework.permissions.IsAuthenticated',),  # 权限
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
    ) if DEBUG else ('rest_framework_jwt.authentication.JSONWebTokenAuthentication',),  # 认证
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',),  # 过滤
    'DEFAULT_PAGINATION_CLASS': 'mes.paginations.DefaultPageNumberPagination',  # 分页
    'DATETIME_FORMAT': "%Y-%m-%d %H:%M:%S",
}

JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(minutes=30),
    'JWT_ALLOW_REFRESH': True,
}

LOGGING_DIR = os.environ.get('LOGGING_DIR', os.path.join(BASE_DIR, 'logs'))
#
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'verbose': {
#             'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
#         },
#         'simple': {
#             'format': '%(levelname)s %(message)s'
#         },
#         'standard': {
#             'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] '
#                       '[%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'
#         },
#         'django_request': {
#             'format': '%(levelname)s %(asctime)s %(pathname)s %(module)s %(lineno)d %(message)s'
#                       ' status_code:%(status_code)d',
#             'datefmt': '%Y-%m-%d %H:%M:%S'
#         },
#         'django_db_backends': {
#             'format': '%(levelname)s %(asctime)s %(pathname)s %(module)s %(lineno)d %(message)s',
#             'datefmt': '%Y-%m-%d %H:%M:%S'
#         },
#     },
#     'filters': {
#         'require_debug_true': {
#             '()': 'django.utils.log.RequireDebugTrue',
#         },
#
#     },
#     'handlers': {
#         'console': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#             'formatter': 'standard'
#         },
#         'django_db_backends': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#             'formatter': 'django_db_backends'
#         },
#         'django_request': {
#             'level': 'DEBUG',
#             'filters': ['require_debug_true'],
#             'class': 'logging.StreamHandler',
#             'formatter': 'django_request'
#         },
#         'timedRotatingFile': {
#             'level': 'DEBUG',
#             'class': 'logging.handlers.TimedRotatingFileHandler',
#             'filename': os.path.join(LOGGING_DIR, 'api_log.log'),
#             'when': 'D',
#             'backupCount': 10,
#             'formatter': 'standard',
#         },
#         'errorFile': {
#             'level': 'DEBUG',
#             'class': 'logging.handlers.TimedRotatingFileHandler',
#             'filename': os.path.join(LOGGING_DIR, 'error.log'),
#             'when': 'D',
#             'backupCount': 10,
#             'formatter': 'standard',
#         },
#     },
#     'loggers': {
#         'django.db.backends': {
#             'handlers': ['django_db_backends'],
#             'propagate': True,
#             'level': 'DEBUG' if DEBUG else 'INFO',
#         },
#         'django.request': {
#             'handlers': ['django_request'],
#             'level': 'ERROR',
#             'propagate': False,
#         },
#         'api_log': {
#             'handlers': ['timedRotatingFile'],
#             'level': 'DEBUG' if DEBUG else 'INFO',
#         },
#         'error_log': {
#             'handlers': ['errorFile'],
#             'level': 'DEBUG' if DEBUG else 'INFO',
#         }
#     },
# }


if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
            'NAME': os.getenv('DATABASE_NAME', 'mes'),  # 数据库名称
            'USER': os.getenv('DATABASE_USERNAME', 'root'),  # 用户名
            'PASSWORD': os.getenv('DATABASE_PASSWORD', 'mes@2020'),  # 密码
            'HOST': os.getenv('DATABASE_HOSTNAME', '10.10.120.14'),  # HOST
            'PORT': os.getenv('MONOCLE_API_PORT', '3306'),  # 端口
        }
    }

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

AUTH_USER_MODEL = 'system.User'
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'

LANGUAGES = (
    ('en-us', ugettext_lazy(u"English")),
    ('zh-hans', ugettext_lazy(u"简体中文")),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

LOGIN_URL = 'gui:login'
LOGIN_REDIRECT_URL = 'gui:global-codes-manage'
LOGOUT_REDIRECT_URL = 'gui:login'
