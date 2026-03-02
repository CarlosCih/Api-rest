
import logging
from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import *
from .serializers import *
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken

# Configura el logger para este módulo
logger = logging.getLogger(__name__)

# Create your views here.
class LoginRateThrottle(AnonRateThrottle):
    scope = 'login'
class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
    
    def post(self, request):
        # Lógica para autenticar al usuario y generar un token JWT
        email = request.data.get('email', None)
        password = request.data.get('password', None)

        user = authenticate(request, email=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)
            logger.info(f"Login exitoso para usuario: {email}")
            return Response({
                'user': UserMeSerializer(user).data,
                'token': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Intento de login fallido para usuario: {email}")
            return Response(
                {'detail': 'Credenciales inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()  # Agrega el token a la lista negra
            
            logger.info(f"Logout exitoso para usuario: {request.user}")
            return Response({
                'detail': 'Logout exitoso'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error durante logout para usuario: {request.user} - {str(e)}")
            return Response({
                'detail': 'Error durante logout'
            }, status=status.HTTP_400_BAD_REQUEST)
class SignUpRateThrottle(AnonRateThrottle):
    scope = 'signup'   

class SignupView(generics.CreateAPIView):
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny] # Permitir acceso sin autenticación para el registro
    throttle_classes = [SignUpRateThrottle]
    
class ProfileView(generics.RetrieveUpdateAPIView):
    http_method_names = ['get','patch']
    
    def get_object(self):
        if self.request.user.is_authenticated:
            return self.request.user
        
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserMeSerializer
        return UserUpdateSerializer