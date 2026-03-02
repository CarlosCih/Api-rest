"""
Configuración de Cache para Django REST API
============================================

Copiar esta configuración al archivo settings apropiado:
- server/config/settings/local.py (desarrollo)
- server/config/settings/prod.py (producción)
"""

# ============================================
# OPCIÓN 1: Redis (RECOMENDADO PRODUCCIÓN)
# ============================================

"""
Instalar dependencias:
pip install redis django-redis

Iniciar Redis:
- Windows: redis-server.exe
- Linux/Mac: redis-server
- Docker: docker run -d -p 6379:6379 redis:alpine
"""

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            # Serializer más rápido
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        },
        'KEY_PREFIX': 'films_api',
        'TIMEOUT': 300,  # 5 minutos por defecto
    }
}

# Para sesiones en Redis (opcional, mejor rendimiento)
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'


# ============================================
# OPCIÓN 2: Memcached (ALTERNATIVA)
# ============================================

"""
Instalar dependencias:
pip install pymemcache

Iniciar Memcached:
- Windows: memcached.exe -m 64
- Linux: memcached -m 64 -p 11211
- Docker: docker run -d -p 11211:11211 memcached:alpine
"""

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
#         'LOCATION': '127.0.0.1:11211',
#         'TIMEOUT': 300,
#         'OPTIONS': {
#             'server_max_value_length': 1024 * 1024 * 2,  # 2MB
#         }
#     }
# }


# ============================================
# OPCIÓN 3: Base de Datos (NO RECOMENDADO)
# ============================================

"""
Solo para desarrollo sin Redis/Memcached
Requiere crear tabla: python manage.py createcachetable
"""

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
#         'LOCATION': 'cache_table',
#         'TIMEOUT': 300,
#     }
# }


# ============================================
# OPCIÓN 4: File System (SOLO DESARROLLO)
# ============================================

"""
Para desarrollo local sin servicios externos
NO usar en producción
"""

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
#         'LOCATION': BASE_DIR / 'cache_files',
#         'TIMEOUT': 300,
#     }
# }


# ============================================
# CONFIGURACIÓN AVANZADA: MÚLTIPLES CACHES
# ============================================

"""
Para separar diferentes tipos de cache
"""

# CACHES = {
#     'default': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/1',
#         'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
#         'KEY_PREFIX': 'films',
#         'TIMEOUT': 300,
#     },
#     'sessions': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/2',
#         'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
#         'KEY_PREFIX': 'session',
#         'TIMEOUT': 86400,  # 24 horas
#     },
#     'api': {
#         'BACKEND': 'django_redis.cache.RedisCache',
#         'LOCATION': 'redis://127.0.0.1:6379/3',
#         'OPTIONS': {'CLIENT_CLASS': 'django_redis.client.DefaultClient'},
#         'KEY_PREFIX': 'api',
#         'TIMEOUT': 300,  # 5 minutos
#     },
# }


# ============================================
# MIDDLEWARE DE CACHE (OPCIONAL)
# ============================================

"""
Cache de página completa (solo para vistas públicas)
Agregar a MIDDLEWARE en settings.py:
"""

# MIDDLEWARE = [
#     'django.middleware.cache.UpdateCacheMiddleware',  # PRIMERO
#     'django.middleware.common.CommonMiddleware',
#     # ... otros middlewares ...
#     'django.middleware.cache.FetchFromCacheMiddleware',  # ÚLTIMO
# ]

# CACHE_MIDDLEWARE_ALIAS = 'default'
# CACHE_MIDDLEWARE_SECONDS = 300
# CACHE_MIDDLEWARE_KEY_PREFIX = 'films_page'


# ============================================
# CONFIGURACIÓN PARA PRODUCCIÓN (Ejemplo con AWS/Azure)
# ============================================

"""
# Redis en AWS ElastiCache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://your-elasticache-endpoint.cache.amazonaws.com:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
    }
}

# Redis en Azure Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'rediss://:your-access-key@your-cache.redis.cache.windows.net:6380/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SSL': True,
        },
    }
}
"""


# ============================================
# TESTING Y DEBUGGING
# ============================================

"""
Para pruebas, usar cache dummy (no guarda nada)
En settings/test.py o conftest.py:
"""

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
#     }
# }


# ============================================
# COMANDOS ÚTILES
# ============================================

"""
# Verificar conexión a Redis
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 30)
>>> cache.get('test')
'value'

# Limpiar cache completo
python manage.py shell
>>> from django.core.cache import cache
>>> cache.clear()

# Ver todas las keys en Redis
redis-cli
> KEYS films_api:*
> FLUSHDB  # Limpiar base de datos actual
> FLUSHALL  # Limpiar todas las bases de datos

# Monitorear Redis en tiempo real
redis-cli MONITOR

# Ver estadísticas Redis
redis-cli INFO stats
"""


# ============================================
# CACHE SELECTIVO POR USUARIO
# ============================================

"""
Para cachear resultados por usuario (ej: mis películas favoritas)
Usar en views.py:
"""

# from django.core.cache import cache
# from django.utils.encoding import force_str

# def get_user_films_cache_key(user_id, filters):
#     filter_str = '_'.join([f"{k}={v}" for k, v in sorted(filters.items())])
#     return f"user_{user_id}_films_{filter_str}"

# class FilmUserViewSet(viewsets.ModelViewSet):
#     def list(self, request, *args, **kwargs):
#         cache_key = get_user_films_cache_key(
#             request.user.id,
#             request.query_params.dict()
#         )
#         cached_data = cache.get(cache_key)
        
#         if cached_data:
#             return Response(cached_data)
        
#         response = super().list(request, *args, **kwargs)
#         cache.set(cache_key, response.data, 300)  # 5 minutos
#         return response


# ============================================
# INVALIDACIÓN DE CACHE
# ============================================

"""
Para invalidar cache cuando se actualizan datos
En models.py o signals:
"""

# from django.db.models.signals import post_save, post_delete
# from django.dispatch import receiver
# from django.core.cache import cache

# @receiver(post_save, sender=Film)
# @receiver(post_delete, sender=Film)
# def invalidate_film_cache(sender, instance, **kwargs):
#     # Invaliar cache de listado de películas
#     cache.delete_pattern('films_api:views.decorators.cache*')
    
#     # O invalidar keys específicas
#     cache.delete(f'film_detail_{instance.id}')
#     cache.delete('film_list_page_1')
