# Generated migration for adding database indexes
# Run: python manage.py makemigrations films --empty
# Then copy this content

from django.db import migrations, models


class Migration(migrations.Migration):
    """
    Migración para agregar índices de base de datos optimizados
    para mejorar el rendimiento de queries comunes.
    """

    dependencies = [
        ('films', '0004_film_average_note_film_favorites'),  # Actualizar con la migración anterior
    ]

    operations = [
        # Índice para búsquedas y filtros por año
        migrations.AddIndex(
            model_name='film',
            index=models.Index(
                fields=['year'],
                name='film_year_idx'
            ),
        ),
        
        # Índice para ordenamiento por favoritos (descendente)
        migrations.AddIndex(
            model_name='film',
            index=models.Index(
                fields=['-favorites'],
                name='film_fav_desc_idx'
            ),
        ),
        
        # Índice para ordenamiento por nota promedio (descendente)
        migrations.AddIndex(
            model_name='film',
            index=models.Index(
                fields=['-average_note'],
                name='film_note_desc_idx'
            ),
        ),
        
        # Índice compuesto para ordenamiento por título y año
        migrations.AddIndex(
            model_name='film',
            index=models.Index(
                fields=['title', 'year'],
                name='film_title_year_idx'
            ),
        ),
        
        # Índice para filtros de usuario por estado
        migrations.AddIndex(
            model_name='filmuser',
            index=models.Index(
                fields=['user', 'state'],
                name='filmuser_state_idx'
            ),
        ),
        
        # Índice para filtros de usuario por favoritos
        migrations.AddIndex(
            model_name='filmuser',
            index=models.Index(
                fields=['user', 'favorite'],
                name='filmuser_fav_idx'
            ),
        ),
        
        # Índice para filtros por película y favoritos (actualizaciones)
        migrations.AddIndex(
            model_name='filmuser',
            index=models.Index(
                fields=['film', 'favorite'],
                name='filmuser_film_fav_idx'
            ),
        ),
    ]


"""
NOTA: Para activar esta migración:

1. Ubicar el número de la última migración en server/apps/films/migrations/
2. Renombrar este archivo con el siguiente número secuencial
   Ejemplo: 0005_add_database_indexes.py
3. Actualizar dependencies con la migración anterior
4. Ejecutar:
   pipenv run migrate migrate films

IMPACTO ESPERADO:
- Búsquedas por año: 5-10x más rápido
- Ordenamiento por favoritos/nota: 3-5x más rápido
- Filtros de usuario: 2-3x más rápido

MONITOREO:
Verificar tamaño de índices con:
SELECT indexname, tablename, indexdef 
FROM pg_indexes 
WHERE tablename IN ('films_film', 'films_filmuser');

Análisis de uso:
EXPLAIN ANALYZE SELECT * FROM films_film ORDER BY favorites DESC LIMIT 20;
"""
