
import logging
from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny
from .models import *
from .serializers import *

# Configura el logger para este módulo
logger = logging.getLogger(__name__)

# Create your views here.

class LoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Lógica para autenticar al usuario y generar un token JWT
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            serializer = UserReadSerializer(user)
            logger.info(f"Login exitoso para usuario: {email}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Intento de login fallido para usuario: {email}")
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        

class LogoutView(APIView):
    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        logout(request)
        logger.info(f"Logout realizado para usuario: {user}")
        return Response(status=status.HTTP_200_OK)

class SignupView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny] # Permitir acceso sin autenticación para el registro
    
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    http_method_names = ['get','patch']
    
    def get_object(self):
        if self.request.user.is_authenticated:
            return self.request.user
        
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserReadSerializer
        return UserUpdateSerializer