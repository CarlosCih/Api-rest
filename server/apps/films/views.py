from django.shortcuts import render
from rest_framework import viewsets, filters, views, status, authentication, permissions
from .models import *
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

# Create your views here.
class ExtendedPagination(PageNumberPagination):
    page_size=8
    
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
            'next_link': next_link,
            'previous_link': previous_link,
            'results': data
        })

class FilmViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer
    
    
    # Sistema de filtros
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'year', 'genres__name']
    ordering_fields = ['title', 'year', 'genres__name']
    filterset_fields = {
        'year': ['lte', 'gte'], # Año menor o igual, año mayor o igual
        'genres': ['exact'], # Género exacto
    }
    
    # Sistema de paginación
    pagination_class = ExtendedPagination
    ordering_fields = ['title', 'year',
                    'genres__name', 'favorites', 'average_note']
    
    
class GenreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = FilmGenre.objects.all()
    serializer_class = FilmGenreSerializer
    lookup_field = 'slug'
    
class FilmUserViewSet(views.APIView):
    authentication_classes = [authentication.SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        queryset = FilmUser.objects.filter(user=request.user)
        serializer = FilmUserSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request, *args, **kwargs):
        try:
            film = Film.objects.get(id=request.data['uuid'])
        except Film.DoesNotExist:
            return Response(
                {'status': 'Film not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        # Al recuperar la película, se crea o actualiza la relación con el usuario
        film_user, created = FilmUser.objects.update_or_create(
            user=request.user, film=film,
        )
        
        # Configuracion de cada campo
        film_user.favorite = request.data.get('favorite', False)
        film_user.state = request.data.get('state', 0)
        film_user.note = request.data.get('note', -1)
        film_user.review = request.data.get('review', None)
        
        # Si hay pelicula como no vista, se borra automaticamente
        if int(film_user.state)==0:
            film_user.delete()
            return Response(
                {'status': 'Deleted'},
                status=status.HTTP_200_OK
            )
        else:
            film_user.save()
            
        return Response(
            {'status': 'Saved'},
            status=status.HTTP_200_OK
        )