from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

def path_to_avatar(instance, filename):
        return f'avatars/{instance.id}/{filename}'

class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']  # Puedes agregar otros campos requeridos aquí
    # Puedes agregar campos personalizados aquí si lo deseas
    email = models.EmailField(
            max_length=150, unique=True, verbose_name='Correo Electrónico'
    )
    avatar = models.ImageField(upload_to=path_to_avatar, null=True, blank=True)


