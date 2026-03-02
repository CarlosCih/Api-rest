from django.db import models
import uuid
from django.utils.text import slugify
from django.conf import settings
from django.core.validators import MaxValueValidator
from django.db.models import Sum, Avg, Count
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
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
    
    def update_stats(self):
        """
        Actualiza estadísticas de la película usando agregaciones eficientes.
        Usa una sola query con agregaciones en lugar de múltiples queries.
        """
        stats = FilmUser.objects.filter(film=self).aggregate(
            total_favorites=Count('id', filter=models.Q(favorite=True)),
            avg_note=Avg('note', filter=models.Q(note__isnull=False))
        )
        
        self.favorites = stats['total_favorites'] or 0
        self.average_note = round(stats['avg_note'], 2) if stats['avg_note'] else 0.0
        self.save(update_fields=['favorites', 'average_note'])
        
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

# ========================================
# Señales para actualización optimizada de estadísticas
# ========================================

# Variable para rastrear cambios relevantes
_filmuser_changes = {}

@receiver(pre_save, sender=FilmUser)
def track_filmuser_changes(sender, instance, **kwargs):
    """
    Detecta cambios en campos relevantes (favorite, note, state) 
    para evitar recalcular estadísticas innecesariamente.
    """
    if instance.pk:  # Solo si es una actualización
        try:
            old_instance = FilmUser.objects.get(pk=instance.pk)
            # Verificar si cambiaron campos que afectan las estadísticas
            has_changes = (
                old_instance.favorite != instance.favorite or
                old_instance.note != instance.note or
                old_instance.state != instance.state
            )
            _filmuser_changes[instance.pk] = {
                'has_changes': has_changes,
                'film_id': instance.film.id
            }
        except FilmUser.DoesNotExist:
            _filmuser_changes[instance.pk] = {
                'has_changes': True,  # Nueva instancia
                'film_id': instance.film.id
            }
    else:
        # Nueva instancia, siempre actualizar
        _filmuser_changes['new'] = {
            'has_changes': True,
            'film_id': instance.film.id
        }

@receiver(post_save, sender=FilmUser)
def update_film_stats_conditional(sender, instance, created, **kwargs):
    """
    Actualiza las estadísticas de la película solo si hubo cambios 
    en campos relevantes (optimización condicional).
    """
    change_key = 'new' if created else instance.pk
    change_info = _filmuser_changes.get(change_key, {})
    
    # Solo recalcular si hubo cambios relevantes
    if change_info.get('has_changes', False):
        instance.film.update_stats()
    
    # Limpiar el tracker
    if change_key in _filmuser_changes:
        del _filmuser_changes[change_key]
    