from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="El correo electrónico ya está en uso."
            )
        ]
    )
    username = serializers.CharField(
        required=True,
        max_length=150,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message="El nombre de usuario ya está en uso."
            )
        ]
    )
    
    password = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
        )
    password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        min_length=8,
        style={'input_type': 'password'},
        label="Confirmar contraseña"
    )
    class Meta:
        model = get_user_model()
        fields = ('email','username','password', 'password_confirm')
        read_only_fields = ('id',)
        
    def validate_username(self, value):
        # Permite eliminar espacios en blanco
        value = value.strip().replace(" ", "")
        if len(value) < 2:
            raise serializers.ValidationError("El nombre de usuario debe tener al menos 2 caracteres.")
        
        # Validacion para evitar unicamente numero
        if value.isdigit():
            raise serializers.ValidationError("El nombre de usuario no puede ser únicamente caracteres numéricos.")
        
        return value
    
    def validate_password(self, value):
        try: 
             validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value
    def validate(self, attrs):
        """Validaciones de cruzadas"""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        username = attrs.get('username')
        email = attrs.get('email')
        
        if password != password_confirm:
            raise serializers.ValidationError({
                "password_confirm": "Las contraseñas no coinciden."
            })
            
        # Validar que password no contenga el username o el email
        if username.lower() in password.lower():
            raise serializers.ValidationError({
                "password": "La contraseña no puede contener el nombre del usuario."
            })
            
        # Validar que password no contenga el email
        email_local = email.split('@')[0]
        if email_local.lower() in password.lower():    
            raise serializers.ValidationError({
                "password": "La contraseña no puede contener el correo electrónico."
            })
            
        attrs.pop('password_confirm')
        return attrs
    
    def create(self, validated_data):
        """Crea el usuario con la contraseña hasheada"""
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user
        
class UserMeSerializer(serializers.ModelSerializer):
    """Serializer para el perfil propio del usuario, sin campos sensibles"""
    
    class Meta:
        model =  User
        fields = ('id','email', 'username','avatar', 'date_joined', 'last_login', 'is_active')
        read_only_fields = fields
        
class UserPublicSerializer(serializers.ModelSerializer):
    """Serializer para perfiles publicos de otros usuarios"""
    
    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'avatar',
            'date_joined',
        )
        read_only_fields = fields
        
class UserUpdateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=False,
        max_length=150,
    )
    avatar = serializers.ImageField(
        required=False,
        allow_null=True
    )
    
    class Meta:
        model = User
        fields = ('id','username', 'avatar')
        read_only_fields = ('id',)
    
    def validate_username(self, value):
        """Valida username con exclusion del usuario actual"""
        value = value.strip().replace(" ", "")
        if len(value) < 2:
            raise serializers.ValidationError("El nombre de usuario debe tener al menos 2 caracteres.")
        
        if User.objects.exclude(pk=self.instance.pk).filter(username=value).exists():
            raise serializers.ValidationError("El nombre de usuario ya está en uso.")
        return value
    
    def validate_avatar(self, value):
        """Valida el tamaño y formato de la imagen"""
        if value:
            # Validar tamaño maximo de 2MB
            if value.size > 2 * 1024 * 1024:
                raise serializers.ValidationError("El tamaño de la imagen no puede superar los 2MB.")
            # Validar formato de imagen
            allowed_formats = ['image/jpeg', 'image/png', 'image/webp']
            if value.content_type not in allowed_formats:
                raise serializers.ValidationError("El formato de la imagen no es valido. Use: JPEG, PNG o WEBP.")  
        return value
