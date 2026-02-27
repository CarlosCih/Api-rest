from pathlib import Path
from datetime import timedelta
import os, environ
env = environ.Env()
environ.Env.read_env()
print("Cargando configuración base...")
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parents[2]
print(f"BASE_DIR: {BASE_DIR}")
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Django external apps
    'rest_framework',
    'rest_framework.authtoken',
    'django_rest_passwordreset',
    'corsheaders',
    'django_filters',
    'drf_spectacular',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    # app personalizada
    'apps.authentication',
    'apps.films',
]
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = 'config.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'
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
# Simple JWT settings
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60), # Duración del token de acceso
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7), # Duración del token
    "ROTATE_REFRESH_TOKENS": True, # Rotar tokens de refresco
    "BLACKLIST_AFTER_ROTATION": True, # Agregar tokens rotados a la lista
    "UPDATE_LAST_LOGIN": True, # Actualizar el campo last_login del usuario al autenticar
}
# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/
LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static_files/'
STATICFILES_DIRS = [
    BASE_DIR / 'static/'
]
# Media files
MEDIA_ROOT = BASE_DIR / 'media/'
MEDIA_URL = '/media/'
AUTH_USER_MODEL = 'authentication.CustomUser'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
REST_FRAMEWORK = {
    #Auth
    "DEFAULT_AUTHENTICATION_CLASSES":[
        "rest_framework_simplejwt.authentication.JWTAuthentication", # Para autenticación basada en JWT
        "rest_framework.authentication.SessionAuthentication", # Para autenticación basada en sesiones (útil para el panel de administración)
    ],
    # Permissions
    # Optional:
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated", # Requiere autenticación para todas las vistas por defecto
    ],
    # Pagination
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10, # Número de resultados por página
    "DEFAULT_RENDERER_CLASSES":[
        "rest_framework.renderers.JSONRenderer", # Renderiza las respuestas en formato JSON
        "rest_framework.renderers.BrowsableAPIRenderer", # Permite la interfaz
    ],
    # Filtros
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend", # Para filtros basados en campos
        "rest_framework.filters.SearchFilter", # Para búsqueda por texto
        "rest_framework.filters.OrderingFilter", # Para ordenamiento de resultados
    ],
    # Formato de fecha/hora
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z", # Formato ISO 8601
    # Versionado de API
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1", "v2"],
    # Exception handler
    "EXCEPTION_HANDLER": "config.exception_handler.custom_exception_handler", 
}
REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'
SPECTACULAR_SETTINGS = {
    'TITLE': 'API de Películas',
    'DESCRIPTION': 'Una API REST para gestionar películas, géneros y usuarios.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}
# Configuracion de Throttling (limitación de tasa)
REST_FRAMEWORK.update({
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.UserRateThrottle", # Limita por usuario autenticado
        "rest_framework.throttling.AnonRateThrottle", # Limita por usuario anónimo
    ],
    "DEFAULT_THROTTLE_RATES": {
        "user": "300/min", # Limite para usuarios autenticados
        "anon": "60/min", # Limite para usuarios anónimos
        "login": "5/min", # Limite específico para intentos de login
    }
})
# Manejo de Logging
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True) # Crear el directorio de logs si no existe
LOGGING ={
    "version":1,
    "disable_existing_loggers": False,
    "formatters":{
        "verbose":{
            "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        },
        "simple":{
            "format": "%(levelname)s | %(name)s | %(message)s"
        },
    },
    "handlers":{
        "console":{
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file":{
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "server.log"),
            "maxBytes": 5 * 1024 * 1024, # 5 MB
            "backupCount": 5, # Mantener los últimos 5 archivos de log
            "formatter": "verbose",
            "encoding": "utf-8",
        },
        "file_error":{
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "server_error.log"),
            "maxBytes": 5 * 1024 * 1024, # 5
            "backupCount": 5, # Mantener los últimos 5 archivos de log
            "formatter": "verbose",
            "encoding": "utf-8",
            "level": "ERROR",
        },
    },
    "loggers":{
        # Django core
        "django":{
            "handlers": ["console","file"],
            "level":"INFO",
            "propagate": True,
        },
        # Errors requests
        "django.request":{
            "handlers":["console","file_error"],
            "level":"ERROR",
            "propagate": False,
        },
        # DRF
        "rest_framework":{
            "handlers": ["console","file"],
            "level":"INFO",
            "propagate": False,
        },
        # App personalizada
        "apps.authentication":{
            "handlers":["console","file"],
            "level":"INFO",
            "propagate": False,
        },
        "apps.films":{
            "handlers":["console","file"],
            "level":"INFO",
            "propagate": False,
        },
    },
}