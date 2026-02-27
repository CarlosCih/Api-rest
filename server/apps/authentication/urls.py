from django.urls import path, include
from .views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    # Endpoints RESTful - recursos en plural
    path('auth/login/', LoginView.as_view(), name='login'),  # POST para login
    path('auth/tokens/delete/', LogoutView.as_view(), name='token-delete'),  # POST para eliminar token (logout)
    path('users/', SignupView.as_view(), name='user-create'),  # POST para crear usuario
    path('users/me/', ProfileView.as_view(), name='user-profile'),  # GET/PATCH para perfil actual
    path('auth/reset/', include('django_rest_passwordreset.urls',  namespace='password_reset')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]