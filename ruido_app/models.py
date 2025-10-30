from django.db import models
from django.utils import timezone

# Create your models here.

class LecturaRuido(models.Model):
    nivel_db = models.FloatField() # valor numérico en decibelios
    fecha_hora = models.DateTimeField(default=timezone.now) # fecha automática
    
    def __str__(self):
        return f"{self.nivel_db} dB - {self.fecha_hora.strftime('%Y-%m-%d %H:%M:%S')}"
