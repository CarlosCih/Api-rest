from rest_framework import serializers
from .models import *
from rest_framework.validators import UniqueTogetherValidator

class FilmGenreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FilmGenre
        fields = ('id','name','slug')
        read_only_fields = fields
        
class FilmListSerializer(serializers.ModelSerializer):
    """Serializer para el listado de peliculas"""
    genre_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        source='genres',
        read_only=True,
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
            'average_note',
        )
        read_only_fields = fields
        
class FilmDetailSerializer(serializers.ModelSerializer):
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

class FilmUserWriteSerializer(serializers.ModelSerializer):
    """Serializer para crear o actualizar la relación usuario-pelicula"""
    
    film_id = serializers.PrimaryKeyRelatedField(
        queryset=Film.objects.all(),
        source='film',
        write_only=True
    )
    class Meta:
        model=FilmUser
        fields=(
            'id',
            'film_id',
            'state',
            'favorite',
            'note',
            'review'
        )
        read_only_fields = ('id',)
        validators = [
            UniqueTogetherValidator(
                queryset=FilmUser.objects.all(),
                fields=('user', 'film'),
                message='Ya existe una relación entre este usuario y esta película.'
            )
        ]
    def validate_note(self, value):
        if value is not None and (value < 0 or value > 10):
            raise serializers.ValidationError('La nota debe estar entre 0 y 10.')
        return value
    def validate_state(self, value):
        validate_states = [
            choice[0] for choice in FilmUser.STATUS_CHOICES
        ]
        if value not in validate_states:
            raise serializers.ValidationError(f'El estado debe ser uno de los siguientes: {", ".join(validate_states)}.')
        return value
    
    def validate(self, attrs):
        note = attrs.get('note')
        state = attrs.get('state')
        if note is not None and note > 0 and state != 1:
            raise serializers.ValidationError({
                'state': "Solo puedes calificar una pelicula que hayas visto (estado 'Vista')."
            })
        if not self.instance:
            request = self.context.get('request')
            if request and hasattr(request, 'user'):
                attrs['user'] = request.user
        return attrs
    
class FilmUserReadSerializer(serializers.ModelSerializer):
    film = FilmListSerializer(read_only=True)
    state_display = serializers.CharField(source='get_state_display', read_only=True)
    
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

            
"""class FilmGenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = FilmGenre
        fields = '__all__'

    class NestedFilmSerializer(serializers.ModelSerializer):

        class Meta:
            model = Film
            fields = ['id', 'title', 'image_thumbnail', 'genres']
            
    films = NestedFilmSerializer(
        many=True, source="film_genres")  # query reversa
    
class FilmSerializer(serializers.ModelSerializer):

    class Meta:
        model = Film
        fields = '__all__'

    class NestedFilmGenreSerializer(serializers.ModelSerializer):

        class Meta:
            model = FilmGenre
            fields = '__all__'

    genres = NestedFilmGenreSerializer(many=True)
    
class FilmUserSerializer(serializers.ModelSerializer):
    film = FilmSerializer(read_only=True)
    
    class Meta:
        model = FilmUser
        fields = ['film', 'favorite', 'note', 'state','review']"""