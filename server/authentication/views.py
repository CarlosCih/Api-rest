from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login, logout
from rest_framework.response import Response
from rest_framework import status, generics
from .serializers import UserSerializer

# Create your views here.
class LoginView(APIView):
    def post(self, request):
        # Lógica para autenticar al usuario y generar un token JWT
        email = request.data.get('email', None)
        password = request.data.get('password', None)
        
        user = authenticate(request, email=email, password=password)
        
        # Si es correcto se añade la información del usuario
        if user is not None:
            login(request,user)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        
class LogoutView(APIView):
    def post(self, request):
        # Lógica para cerrar sesión del usuario
        logout(request)
        return Response(status=status.HTTP_200_OK)

class SignupView(generics.CreateAPIView):
    serializer_class = UserSerializer
    
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    http_method_names = ['get','patch']
    
    def get_object(self):
        if self.request.user.is_authenticated:
            return self.request.user