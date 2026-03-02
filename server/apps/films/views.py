import logging
from django.shortcuts import render
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
    queryset = Film.objects.all()
    serializer_class = FilmSerializer        
    # Sistema de filtros
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'year', 'genres__name']
    filterset_fields = {
        'year': ['lte', 'gte'], # Año menor o igual, año mayor o igual
        'genres': ['exact'], # Género exacto
    }    
    # Sistema de paginación
    pagination_class = ExtendedPagination
    ordering_fields = ['title', 'year','genres__name', 'favorites', 'average_note'] # Campos por los que se puede ordenar
class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FilmGenre.objects.all()
    serializer_class = FilmGenreSerializer
    lookup_field = 'slug'
    pagination_class = ExtendedPagination
    

class FilmUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar las películas del usuario (favoritos, estados, notas, reviews)
    """
    serializer_class = FilmUserSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        """Retorna solo las películas del usuario autenticado"""
        return FilmUser.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Asocia automáticamente el usuario al crear una relación película-usuario"""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """Al actualizar, si el estado es 0 (sin estado), elimina la relación"""
        if serializer.validated_data.get('state') == 0:
            serializer.instance.delete()
            logger.info(f"FilmUser entry deleted for user {self.request.user} and film {serializer.instance.film.id}")
        else:
            serializer.save()
            logger.info(f"FilmUser entry updated for user {self.request.user} and film {serializer.instance.film.id}")