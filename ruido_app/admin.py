from django.contrib import admin
from .models import LecturaRuido, Edificio, Dispositivo

# Register your models here.
from django.contrib import admin
from .models import Edificio, Dispositivo, LecturaRuido

@admin.register(Edificio)
class EdificioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'usuario')

@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ubicacion', 'edificio', 'api_key')
    search_fields = ('nombre', 'edificio__nombre')

@admin.register(LecturaRuido)
class LecturaRuidoAdmin(admin.ModelAdmin):
    list_display = ('dispositivo', 'fecha_hora', 'nivel_db')
    list_filter = ('dispositivo__edificio',)
    ordering = ('-fecha_hora',)
