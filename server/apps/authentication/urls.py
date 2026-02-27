from django.urls import path, include
from .views import *

urlpatterns = [
    # Endpoints RESTful - recursos en plural
    path('auth/tokens/', LoginView.as_view(), name='token-create'),  # POST para crear token (login)
    path('auth/tokens/delete/', LogoutView.as_view(), name='token-delete'),  # POST para eliminar token (logout)
    path('users/', SignupView.as_view(), name='user-create'),  # POST para crear usuario
    path('users/me/', ProfileView.as_view(), name='user-profile'),  # GET/PATCH para perfil actual
    path('auth/reset/', include('django_rest_passwordreset.urls',  namespace='password_reset')),
]