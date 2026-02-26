from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, min_length=8)
    avatar = serializers.ImageField(required=False, allow_null=True)
    
    def update(self, instance, validated_data):
        validated_data.pop('email', None)
        return super().update(instance, validated_data)
    
    def validate_password(self, value):
        # Aqui puedes agregar validaciones adicionales para la contraseña si lo deseas
        return make_password(value)
    
    def validate_username(self, value):
        value = value.replace(" ", "")
        try:
            user = get_user_model().objects.get(username=value)
            # si el mismo usuario manda su username no se lanza el error
            if user == self.instance:
                return value
        except get_user_model().DoesNotExist:
            return value    
        raise serializers.ValidationError("El nombre de usuario ya está en uso.")
    
    def validate_email(self, value):
        try:
            user = get_user_model().objects.get(email=value)
            # si el mismo usuario manda su email no se lanza el error
            if user == self.instance:
                return value
        except get_user_model().DoesNotExist:
            return value
        raise serializers.ValidationError("El correo electrónico ya está en uso.")
    
    class Meta:
        model = get_user_model()
        fields = ('email', 'username', 'password', 'avatar')