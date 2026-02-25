from django.db import models
import uuid
from django.utils.text import slugify
from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db.models import Sum
from django.db.models.signals import post_save
# Create your models here.
class Film(models.Model):
    def path_to_film(self, instance, filename):
        return f'films/{instance.id}/{filename}'
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=150, verbose_name='Titulo')
    year = models.PositiveIntegerField(verbose_name='Año', default=2000)
    review_short = models.TextField(verbose_name='Reseña corta', blank=True, null=True)
    review_large = models.TextField(verbose_name='Reseña larga', blank=True, null=True)
    trailer_url = models.URLField(verbose_name='URL del trailer', blank=True, null=True, max_length=150)
    genres = models.ManyToManyField('FilmGenre', related_name='film_genres', verbose_name='Géneros')
    image_thumbnail = models.ImageField(
        upload_to=path_to_film, null=True, blank=True, verbose_name="Miniatura")
    image_wallpaper = models.ImageField(
        upload_to=path_to_film, null=True, blank=True, verbose_name="Wallpaper")
    # Estadisticas actualizadas con señales
    favorites = models.IntegerField(
        default=0, verbose_name="favoritos")
    average_note = models.FloatField(
        default=0.0, verbose_name="nota media", 
        validators=[MaxValueValidator(10.0)])
        
    def update_film_stats(sender, instance, **kwargs):
        # # Actualizamos los favoritos contando los favoritos de esa película
        count_favorites = FilmUser.objects.filter(
            film=instance.film, favorite=True).count()
        instance.film.favorites = count_favorites
        # Actualizamos la nota recuperando el número de notas y haciendo la media
        notes = FilmUser.objects.filter(
            film=instance.film).exclude(note__isnull=True)
        count_notes = notes.count()
        sum_notes = notes.aggregate(Sum('note')).get('note__sum')
        try:
            instance.film.average_note = round(sum_notes/count_notes, 2)
        except:
            pass
        instance.film.save()
        
    class Meta:
        verbose_name = 'Película'
        verbose_name_plural = 'Películas'
        ordering = ['title']
        
    def __str__(self):
        return f'{self.title} ({self.year})'

    
class FilmGenre(models.Model):
    name = models.CharField(max_length=50, verbose_name='Nombre del género', unique=True)
    slug = models.SlugField(unique=True) 
    
    class Meta:
        verbose_name = 'Género de película'
        verbose_name_plural = 'Géneros de película'
        ordering = ['name']
        
    def __str__(self):
        return f'{self.name}'
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(FilmGenre, self).save(*args, **kwargs)
        
class FilmUser(models.Model):
    STATUS_CHOICES = [
        (0, "Sin estado"),
        (1, "Vista"),
        (2, "Quiero ver"),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuario')
    film = models.ForeignKey(Film, on_delete=models.CASCADE, verbose_name='Película')
    state = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0, verbose_name='Estado')
    favorite = models.BooleanField(default=False, verbose_name='Favorita')
    note = models.PositiveSmallIntegerField(null=True, validators=[MaxValueValidator(10)], verbose_name='Nota')
    review = models.TextField(null=True, blank=True, verbose_name='Reseña personal')
    
    class Meta: 
        unique_together = ('user', 'film')
        ordering = ['film__title']

# Conectar la señal para actualizar estadísticas de películas
post_save.connect(Film.update_film_stats, sender=FilmUser)
    