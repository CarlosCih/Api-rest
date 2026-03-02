import logging
from django.shortcuts import render
from django.db.models import Prefetch, Avg, Count
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework import viewsets, filters, views, status, authentication, permissions
from .models import *
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from config.pagination import StandardPagination
from .permissions import IsOwner
import logging
# Configura el logger para este módulo
logger = logging.getLogger(__name__)
# Create your views here.
class ExtendedPagination(StandardPagination):
    """Paginación extendida con información adicional"""

    def get_paginated_response(self, data):
        # Valores por defectos
        next_link = self.get_next_link()
        previous_link = self.get_previous_link()       
        # Split en la primera "/" para obtener solo los parametros
        if next_link:
            next_link = next_link.split("?")[-1]
        if previous_link:
            previous_link = previous_link.split("?")[-1]        
        return Response({
            'count': self.page.paginator.count,
            'num_pages': self.page.paginator.num_pages,
            'page_number': self.page.number,
            'page_size': self.page_size,
            'next': next_link,  # Nombres estándar de DRF
            'previous': previous_link,
            'results': data
        })
class FilmViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet optimizado para películas con:
    - Prefetch optimizado de géneros
    - Cache en listados comunes (5 minutos)
    - Búsqueda optimizada (TODO: usar full-text search en Postgres)
    - Ordenamiento por estadísticas calculadas
    """
    pagination_class = ExtendedPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    # TODO: Migrar a full-text search de Postgres para mejor performance
    # search_fields con trigram similarity: ['title', 'year', 'genres__name']
    search_fields = ['title', 'year', 'genres__name']
    filterset_fields = {
        'year': ['lte', 'gte'],
        'genres': ['exact'],
    }
    ordering_fields = ['title', 'year', 'genres__name', 'favorites', 'average_note']
    
    def get_queryset(self):
        """Optimización de queries con prefetch_related"""
        return Film.objects.prefetch_related(
            Prefetch('genres', queryset=FilmGenre.objects.only('id', 'name', 'slug'))
        ).all()
    
    @method_decorator(cache_page(60 * 5))  # Cache de 5 minutos
    def list(self, request, *args, **kwargs):
        """Cache para listados comunes (filtros populares)"""
        return super().list(request, *args, **kwargs)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return FilmListSerializer  # Sin nested (performance)
        return FilmDetailSerializer  # Con nested completo

class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet optimizado para géneros con prefetch de películas"""
    lookup_field = 'slug'
    pagination_class = ExtendedPagination
    
    def get_queryset(self):
        """Optimización: prefetch solo campos necesarios"""
        if self.action == 'retrieve':
            # Para detalle, traer películas completas
            return FilmGenre.objects.prefetch_related(
                Prefetch(
                    'film_genres',
                    queryset=Film.objects.only(
                        'id', 'title', 'year', 'review_short', 
                        'image_thumbnail', 'favorites', 'average_note'
                    ).prefetch_related('genres')
                )
            ).annotate(films_count=Count('film_genres'))
        # Para listado, no traer películas
        return FilmGenre.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return FilmGenreDetailSerializer  # Con películas
        return FilmGenreListSerializer  # Solo género
    

class FilmUserViewSet(viewsets.ModelViewSet):
    """ViewSet optimizado para relaciones usuario-película"""
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        """Optimización: select_related + prefetch para reducir queries"""
        return FilmUser.objects.filter(
            user=self.request.user
        ).select_related('film').prefetch_related(
            Prefetch(
                'film__genres',
                queryset=FilmGenre.objects.only('id', 'name', 'slug')
            )
        )
    
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