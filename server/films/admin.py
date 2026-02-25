from django.contrib import admin
from .models import *

# Register your models here.
@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ('title', 'year')
    search_fields = ('title', 'year')
    filter_horizontal = ('genres',)
@admin.register(FilmGenre)
class FilmGenreAdmin(admin.ModelAdmin):
    readonly_fields = ('slug',)
    list_display = ('name',)
    search_fields = ('name',)
