from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Edificio, Dispositivo, LecturaRuido


# -----------------------------
#   USER + CAMPO EDIFICIO
# -----------------------------
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Asignación', {
            'fields': ('edificio',),
        }),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_edificio')

    def get_edificio(self, obj):
        return obj.edificio.nombre if obj.edificio else "Sin asignar"

    get_edificio.short_description = "Edificio"


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


# -----------------------------
#   ADMIN DE EDIFICIO
# -----------------------------
@admin.register(Edificio)
class EdificioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'lista_usuarios')

    def lista_usuarios(self, obj):
        usuarios = obj.usuarios.all()
        if usuarios:
            return ", ".join([u.username for u in usuarios])
        return "Sin usuarios"

    lista_usuarios.short_description = "Usuarios"


# -----------------------------
#   ADMIN DE DISPOSITIVOS
# -----------------------------
@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ubicacion', 'edificio', 'api_key')


# -----------------------------
#   ADMIN DE LECTURAS
# -----------------------------
@admin.register(LecturaRuido)
class LecturaRuidoAdmin(admin.ModelAdmin):
    list_display = ('dispositivo', 'nivel_db', 'fecha_hora')
