from django.db import models
from django.contrib.auth.models import User


class Edificio(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    direccion = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre


# ✔ Cada usuario pertenece a UN edificio (relación muchos a uno)
User.add_to_class(
    'edificio',
    models.ForeignKey(
        Edificio,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="usuarios"
    )
)


class Dispositivo(models.Model):
    nombre = models.CharField(max_length=50)
    ubicacion = models.CharField(max_length=100)
    edificio = models.ForeignKey(
        Edificio,
        on_delete=models.CASCADE,
        related_name='dispositivos'
    )
    api_key = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return f"{self.nombre} ({self.edificio.nombre})"


class LecturaRuido(models.Model):
    dispositivo = models.ForeignKey(
        'Dispositivo',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='lecturas'
    )
    nivel_db = models.FloatField()
    presencia = models.BooleanField(default=False)  # 🔹 NUEVO CAMPO
    fecha_hora = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dispositivo} - {self.nivel_db} dB"
