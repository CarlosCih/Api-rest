"""
URL configuration for server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from rest_framework import routers
from django.urls import path, include
from django.conf.urls.static import static
from apps.films import views as film_views
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


# Router para las vistas de la app films
router = routers.DefaultRouter()
router.register('films', film_views.FilmViewSet, basename='films')
router.register('genres', film_views.GenreViewSet, basename='genres')
router.register('user-film', film_views.FilmUserViewSet, basename='user-film')


urlpatterns = [
    path('admin/', admin.site.urls),
    #API versioning
    path('api/v1/', include('apps.authentication.urls')),
    path('api/v1/', include(router.urls)),    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
