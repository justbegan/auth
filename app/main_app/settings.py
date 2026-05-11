from pathlib import Path
import os
import sys
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name: str, default: bool = False) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


SECRET_KEY = os.environ.get('SECRET_KEY')
GDAL_LIBRARY_PATH = os.environ.get('GDAL_LIBRARY_PATH')
GEOS_LIBRARY_PATH = os.environ.get('GEOS_LIBRARY_PATH')
PROJ_LIB = os.environ.get('PROJ_LIB') or os.environ.get('PROJ_DATA')
GDAL_DATA = os.environ.get('GDAL_DATA')
if PROJ_LIB:
    os.environ['PROJ_LIB'] = PROJ_LIB
    os.environ['PROJ_DATA'] = PROJ_LIB
if GDAL_DATA:
    os.environ['GDAL_DATA'] = GDAL_DATA
# Если любой символ появиться в env файле то True
# Например DEBUG=False - Это True
# На проде всегда False
DEBUG = env_bool('DEBUG', False)
origins = os.getenv('CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = origins.split(',') if origins else []
# Важно! на проде добавить ссылку
if DEBUG:
    ALLOWED_HOSTS = ['*']
    CORS_ALLOW_ALL_ORIGINS = True
else:
    ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    CORS_ALLOWED_ORIGINS = [origin for origin in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if origin]

    SECURE_SSL_REDIRECT = not DEBUG
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SESSION_COOKIE_SECURE = not DEBUG
    CSRF_COOKIE_SECURE = not DEBUG


# Приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.postgres',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'drf_spectacular',
    'django_filters',
    'rest_framework',
    'djoser',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'corsheaders',
    'django_dump_load_utf8',
    'codemirror2',
    'jsoneditor',
    'simple_history',
    'core',
    # Пользовательские приложения
    'apps.profile',
    'apps.auth',
    'apps.user',
    'apps.admin_panel',
    'apps.business',
    'apps.city',
    'apps.board',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'main_app.custom_middleware.Process500',  # Для отабражение всех ошибок на фронте
    'simple_history.middleware.HistoryRequestMiddleware',
]

AUTH_USER_MODEL = 'user.CustomUser'

ROOT_URLCONF = 'main_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'main_app.wsgi.application'
ASGI_APPLICATION = 'main_app.asgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_HOST'),
        'PORT': os.environ.get('POSTGRES_PORT'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Asia/Yakutsk'

USE_I18N = True

USE_TZ = True


STATIC_URL = '/django-static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "staticfiles"),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': (
                '%(levelname)s %(asctime)s %(name)s '
                '%(module)s %(process)d %(thread)d %(message)s'
            ),
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'stream': sys.stdout,
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.server': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'core.base.pagination.DataPagination',
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'PAGE_SIZE': 20
}

SIMPLE_JWT = {
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    # Врямя жизни токена
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.environ.get("ACCESS_TOKEN_LIFETIME", "5"))),
    # Время жизни рефреш токена
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.environ.get("REFRESH_TOKEN_LIFETIME", "7"))),
}

PLUSOFON_WEBHOOK_TOKEN = os.environ.get('PLUSOFON_WEBHOOK_TOKEN', '')

REDIS_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/1')
REDIS_CHANNELS_URL = os.environ.get('REDIS_CHANNELS_URL', 'redis://redis:6379/2')
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', REDIS_URL)
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', REDIS_URL)
CELERY_TASK_ALWAYS_EAGER = env_bool('CELERY_TASK_ALWAYS_EAGER', False)
CELERY_TIMEZONE = TIME_ZONE

CACHES = {
    'default': {
        'BACKEND': os.environ.get('CACHE_BACKEND', 'django_redis.cache.RedisCache'),
        'LOCATION': os.environ.get('CACHE_LOCATION', REDIS_URL),
        'TIMEOUT': int(os.environ.get('CACHE_TIMEOUT', '300')),
        'KEY_PREFIX': os.environ.get('CACHE_KEY_PREFIX', 'django_template'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    }
}

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [REDIS_CHANNELS_URL],
        },
    },
}

OPENSEARCH_URL = os.environ.get('OPENSEARCH_URL', 'http://opensearch:9200')
OPENSEARCH_INDEX_BUSINESSES = os.environ.get('OPENSEARCH_INDEX_BUSINESSES', 'businesses')
OPENSEARCH_INDEX_PRODUCTS = os.environ.get('OPENSEARCH_INDEX_PRODUCTS', 'products')
OPENSEARCH_INDEX_BOARD = os.environ.get('OPENSEARCH_INDEX_BOARD', 'board_listings')

SPECTACULAR_SERVERS = os.environ.get('SPECTACULAR_SERVERS', '').split(',')

SPECTACULAR_SETTINGS = {
    'TITLE': 'GOROD+',
    'DESCRIPTION': 'API GOROD+',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SECURITY': [{'BearerAuth': []}],
    "SERVERS": [{"url": url} for url in SPECTACULAR_SERVERS],
    'ENUM_NAME_OVERRIDES': {
        'UserStatusEnum': [
            ('active', 'Активен'),
            ('blocked', 'Заблокирован'),
            ('deleted', 'Удален'),
        ],
        'BusinessStatusEnum': [
            ('draft', 'Черновик'),
            ('pending', 'На модерации'),
            ('active', 'Активен'),
            ('rejected', 'Отклонен'),
            ('blocked', 'Заблокирован'),
        ],
        'ModerationStatusEnum': [
            ('pending', 'На рассмотрении'),
            ('approved', 'Одобрено'),
            ('rejected', 'Отклонено'),
        ],
        'ReportStatusEnum': [
            ('pending', 'Новая'),
            ('resolved', 'Решена'),
            ('rejected', 'Отклонена'),
        ],
        'AdCampaignStatusEnum': [
            ('draft', 'Черновик'),
            ('active', 'Активна'),
            ('paused', 'На паузе'),
            ('finished', 'Завершена'),
        ],
        'ProductImportStatusEnum': [
            ('queued', 'В очереди'),
            ('processing', 'В обработке'),
            ('done', 'Готово'),
            ('failed', 'Ошибка'),
        ],
        'OrderStatusEnum': [
            ('created', 'Создан'),
            ('confirmed', 'Подтвержден'),
            ('working', 'В работе'),
            ('ready', 'Готов'),
            ('delivering', 'Доставляется'),
            ('completed', 'Завершен'),
            ('cancelled', 'Отменен'),
        ],
        'PublicationStatusEnum': [
            ('published', 'Опубликован'),
            ('hidden', 'Скрыт'),
            ('deleted', 'Удален'),
            ('pending', 'На модерации'),
        ],
        'StoryStatusEnum': [
            ('active', 'Активна'),
            ('hidden', 'Скрыта'),
            ('expired', 'Истекла'),
        ],
        'BoardListingStatusEnum': [
            ('draft', 'Черновик'),
            ('review', 'На модерации'),
            ('active', 'Активно'),
            ('paused', 'На паузе'),
            ('sold', 'Продано'),
            ('rejected', 'Отклонено'),
            ('deleted', 'Удалено'),
        ],
    },
}
