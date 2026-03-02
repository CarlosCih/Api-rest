# ============================================================================
# EJEMPLOS DE MEJORAS - AUDITORÍA DE SERIALIZERS
# ============================================================================

from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

# ============================================================================
# EJEMPLO #1: UserCreateSerializer - VERSION MEJORADA
# ============================================================================
# Mejoras aplicadas:
# - UniqueValidator para email/username (evita condiciones de carrera)
# - validate_password con validaciones de Django
# - create() que hashea password correctamente
# - Validación cruzada username/email similares
# ============================================================================

User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="El correo electrónico ya está en uso."
            )
        ]
    )
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="El nombre de usuario ya está en uso."
            )
        ]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password', 'password_confirm')
        read_only_fields = ('id',)

    def validate_username(self, value):
        """Limpia y valida el username"""
        # Eliminar espacios
        value = value.strip().replace(" ", "")
        
        if len(value) < 3:
            raise serializers.ValidationError(
                "El nombre de usuario debe tener al menos 3 caracteres."
            )
        
        # Validar que no contenga solo números
        if value.isdigit():
            raise serializers.ValidationError(
                "El nombre de usuario no puede contener solo números."
            )
            
        return value

    def validate_password(self, value):
        """Valida la complejidad de la contraseña usando validators de Django"""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        """Validaciones cruzadas"""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        username = attrs.get('username')
        email = attrs.get('email')

        # Validar que las contraseñas coincidan
        if password != password_confirm:
            raise serializers.ValidationError({
                "password_confirm": "Las contraseñas no coinciden."
            })

        # Validar que password no sea muy similar al username
        if username.lower() in password.lower():
            raise serializers.ValidationError({
                "password": "La contraseña no puede ser similar al nombre de usuario."
            })

        # Validar que password no contenga el email
        email_local = email.split('@')[0]
        if email_local.lower() in password.lower():
            raise serializers.ValidationError({
                "password": "La contraseña no puede contener tu correo electrónico."
            })

        # Remover password_confirm antes de create (no es campo del modelo)
        attrs.pop('password_confirm')
        return attrs

    def create(self, validated_data):
        """Crea el usuario con password hasheado correctamente"""
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']  # create_user hashea automáticamente
        )
        return user


# ============================================================================
# EJEMPLO #2: UserUpdateSerializer - VERSION MEJORADA
# ============================================================================
# Mejoras aplicadas:
# - UniqueValidator con exclusión del usuario actual (para PATCH)
# - Validación de username (consistente con create)
# - read_only_fields explícito
# - Manejo de avatar con validación de tamaño
# ============================================================================

class UserUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=False,
        max_length=150,
    )
    avatar = serializers.ImageField(
        required=False,
        allow_null=True
    )

    class Meta:
        model = User
        fields = ('id', 'username', 'avatar')
        read_only_fields = ('id',)

    def validate_username(self, value):
        """Valida username con exclusión del usuario actual"""
        value = value.strip().replace(" ", "")
        
        if len(value) < 3:
            raise serializers.ValidationError(
                "El nombre de usuario debe tener al menos 3 caracteres."
            )
        
        # Validar unicidad excluyendo el usuario actual
        if User.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
            raise serializers.ValidationError(
                "El nombre de usuario ya está en uso."
            )
            
        return value

    def validate_avatar(self, value):
        """Valida tamaño y formato del avatar"""
        if value:
            # Validar tamaño máximo (2MB)
            if value.size > 2 * 1024 * 1024:
                raise serializers.ValidationError(
                    "El tamaño del avatar no puede superar 2MB."
                )
            
            # Validar formato
            allowed_formats = ['image/jpeg', 'image/png', 'image/webp']
            if value.content_type not in allowed_formats:
                raise serializers.ValidationError(
                    "Formato no permitido. Use: JPG, PNG o WEBP."
                )
        
        return value


# ============================================================================
# EJEMPLO #3: UserReadSerializer - SEPARADO EN Me vs Public
# ============================================================================
# Mejoras aplicadas:
# - Separación de contextos: propio perfil vs perfil público
# - Campos explícitos (no depende del modelo)
# - Read-only explícito
# - Campos sensibles solo en "Me"
# ============================================================================

class UserMeSerializer(serializers.ModelSerializer):
    """Serializer para el perfil propio del usuario autenticado"""
    
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'avatar',
            'date_joined',
            'last_login',
            'is_active'
        )
        read_only_fields = fields  # Todos read-only


class UserPublicSerializer(serializers.ModelSerializer):
    """Serializer para perfiles públicos de otros usuarios"""
    
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'avatar',
            'date_joined'  # Solo fecha de registro, no last_login
        )
        read_only_fields = fields


# ============================================================================
# EJEMPLO #4: FilmSerializer - SEPARADO EN List vs Detail
# ============================================================================
# Mejoras aplicadas:
# - Eliminación de fields='__all__'
# - Separación List (sin nested) vs Detail (con nested)
# - Nested serializers extraídos a top-level
# - Performance optimizado (List sin nested = menos queries)
# ============================================================================

from apps.films.models import Film, FilmGenre

class FilmGenreListSerializer(serializers.ModelSerializer):
    """Serializer simple para géneros en listados"""
    
    class Meta:
        model = FilmGenre
        fields = ('id', 'name', 'slug')
        read_only_fields = fields


class FilmListSerializer(serializers.ModelSerializer):
    """Serializer para listado de películas (sin nested, performance)"""
    genre_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        source='genres',
        read_only=True
    )
    
    class Meta:
        model = Film
        fields = (
            'id',
            'title',
            'year',
            'review_short',
            'image_thumbnail',
            'genre_ids',
            'favorites',
            'average_note'
        )
        read_only_fields = fields


class FilmDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle de película (con nested completo)"""
    genres = FilmGenreListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Film
        fields = (
            'id',
            'title',
            'year',
            'review_short',
            'review_large',
            'trailer_url',
            'genres',
            'image_thumbnail',
            'image_wallpaper',
            'favorites',
            'average_note'
        )
        read_only_fields = fields


# ============================================================================
# EJEMPLO #5: FilmUserSerializer - VERSION MEJORADA
# ============================================================================
# Mejoras aplicadas:
# - Separación read/write para film (nested en read, PK en write)
# - Validaciones de note (0-10)
# - Validaciones de state (choices)
# - Validación cruzada note + state
# - UniqueTogetherValidator para user+film
# - context["request"].user para validación de ownership
# ============================================================================

from apps.films.models import FilmUser
from rest_framework.validators import UniqueTogetherValidator

class FilmUserWriteSerializer(serializers.ModelSerializer):
    """Serializer para crear/actualizar relación usuario-película"""
    film_id = serializers.PrimaryKeyRelatedField(
        queryset=Film.objects.all(),
        source='film',
        write_only=True
    )
    
    class Meta:
        model = FilmUser
        fields = ('id', 'film_id', 'state', 'favorite', 'note', 'review')
        read_only_fields = ('id',)
        validators = [
            UniqueTogetherValidator(
                queryset=FilmUser.objects.all(),
                fields=('user', 'film'),
                message="Ya tienes una relación con esta película."
            )
        ]

    def validate_note(self, value):
        """Valida que la nota esté entre 0 y 10"""
        if value is not None:
            if value < 0 or value > 10:
                raise serializers.ValidationError(
                    "La nota debe estar entre 0 y 10."
                )
        return value

    def validate_state(self, value):
        """Valida que el estado sea válido"""
        valid_states = [choice[0] for choice in FilmUser.STATUS_CHOICES]
        if value not in valid_states:
            raise serializers.ValidationError(
                f"Estado inválido. Opciones: {valid_states}"
            )
        return value

    def validate(self, attrs):
        """Validaciones cruzadas"""
        note = attrs.get('note')
        state = attrs.get('state')
        
        # Si hay nota, debe estar marcada como vista
        if note is not None and note > 0 and state != 1:
            raise serializers.ValidationError({
                "state": "Solo puedes calificar películas que hayas visto. Marca el estado como 'Vista'."
            })
        
        # Agregar user del contexto (para create)
        if not self.instance:  # Solo en create
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                attrs['user'] = request.user
        
        return attrs


class FilmUserReadSerializer(serializers.ModelSerializer):
    """Serializer para leer relación usuario-película (con film nested)"""
    film = FilmListSerializer(read_only=True)
    state_display = serializers.CharField(
        source='get_state_display',
        read_only=True
    )
    
    class Meta:
        model = FilmUser
        fields = (
            'id',
            'film',
            'state',
            'state_display',
            'favorite',
            'note',
            'review'
        )
        read_only_fields = fields


# ============================================================================
# EJEMPLO #6: FilmGenreDetailSerializer - Con películas nested optimizado
# ============================================================================

class FilmGenreDetailSerializer(serializers.ModelSerializer):
    """Serializer para detalle de género con películas (paginadas)"""
    films = FilmListSerializer(
        many=True,
        source='film_genres',  # Related name
        read_only=True
    )
    films_count = serializers.IntegerField(
        source='film_genres.count',
        read_only=True
    )
    
    class Meta:
        model = FilmGenre
        fields = ('id', 'name', 'slug', 'films_count', 'films')
        read_only_fields = fields


# ============================================================================
# EJEMPLO #7: Normalización de errores en exception handler
# ============================================================================
# Mejoras:
# - Siempre retorna formato consistente {"error_id": ..., "errors": {}}
# - Distingue field errors vs non_field_errors
# ============================================================================

"""
Reemplazar en: server/config/exception_handler.py

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
import uuid
import logging

logger = logging.getLogger(__name__)

def custom_exception_handler(exc, context):
    request = context.get("request")
    response = exception_handler(exc, context)

    error_id = str(uuid.uuid4())

    if response is not None:
        # Normalizar errores a formato consistente
        errors = {}
        
        if isinstance(response.data, dict):
            # Si es dict, mantener la estructura
            errors = response.data
        elif isinstance(response.data, list):
            # Si es lista, poner en non_field_errors
            errors = {"non_field_errors": response.data}
        else:
            # Cualquier otro caso
            errors = {"detail": str(response.data)}
        
        data = {
            "error_id": error_id,
            "errors": errors,
        }
        
        logger.warning(
            "API error",
            extra={
                "error_id": error_id,
                "path": getattr(request, "path", None),
                "method": getattr(request, "method", None),
                "status_code": response.status_code,
            },
        )
        return Response(data, status=response.status_code)

    # Errores no controlados (500)
    logger.exception(
        "Unhandled exception",
        extra={
            "error_id": error_id,
            "path": getattr(request, "path", None),
            "method": getattr(request, "method", None),
        },
    )
    return Response(
        {
            "error_id": error_id,
            "errors": {"detail": "Internal server error"}
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
"""

# ============================================================================
# EJEMPLO #8: ViewSet con prefetch_related para evitar N+1
# ============================================================================

"""
Reemplazar en: server/apps/films/views.py

class FilmViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Film.objects.prefetch_related('genres').all()
    pagination_class = ExtendedPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'year', 'genres__name']
    filterset_fields = {
        'year': ['lte', 'gte'],
        'genres': ['exact'],
    }
    ordering_fields = ['title', 'year', 'genres__name', 'favorites', 'average_note']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FilmListSerializer  # Sin nested (performance)
        return FilmDetailSerializer  # Con nested completo


class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FilmGenre.objects.prefetch_related(
        'film_genres__genres'  # Prefetch relaciones nested
    ).all()
    lookup_field = 'slug'
    pagination_class = ExtendedPagination
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FilmGenreDetailSerializer  # Con películas
        return FilmGenreListSerializer  # Solo género


class FilmUserViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        return FilmUser.objects.filter(
            user=self.request.user
        ).select_related('film').prefetch_related('film__genres')
    
    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return FilmUserWriteSerializer
        return FilmUserReadSerializer
    
    def perform_create(self, serializer):
        # Ya no necesario, user se agrega en serializer.validate()
        serializer.save()
    
    def perform_update(self, serializer):
        # Mover lógica a serializer o service
        if serializer.validated_data.get('state') == 0:
            # Si estado es "sin estado", eliminar la relación
            serializer.instance.delete()
            logger.info(
                f"FilmUser entry deleted for user {self.request.user} "
                f"and film {serializer.instance.film.id}"
            )
        else:
            serializer.save()
"""

# ============================================================================
# FIN DE EJEMPLOS
# ============================================================================
