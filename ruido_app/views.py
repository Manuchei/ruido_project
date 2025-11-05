from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from .models import LecturaRuido, Dispositivo, Edificio
import json


@login_required
def home(request):
    # Si es admin, muestra todos los edificios
    if request.user.is_superuser:
        lecturas = LecturaRuido.objects.order_by('-fecha_hora')[:50]
    else:
        # Si es usuario de edificio, solo sus dispositivos
        edificio = getattr(request.user, 'edificio', None)
        if not edificio:
            lecturas = []
        else:
            lecturas = LecturaRuido.objects.filter(
                dispositivo__edificio=edificio
            ).order_by('-fecha_hora')[:50]

    return render(request, 'index.html', {'lecturas': lecturas})


@csrf_exempt
def recibir_ruido(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            nivel = float(data.get('nivel_db'))
            api_key = data.get('api_key')

            # Buscar dispositivo por api_key
            dispositivo = Dispositivo.objects.filter(api_key=api_key).first()
            if not dispositivo:
                return JsonResponse({'status': 'error', 'message': 'Dispositivo no encontrado'}, status=400)

            # Crear lectura
            LecturaRuido.objects.create(dispositivo=dispositivo, nivel_db=nivel)

            # Limpieza automática (24h)
            limite = timezone.now() - timedelta(hours=24)
            LecturaRuido.objects.filter(fecha_hora__lt=limite).delete()

            return JsonResponse({'status': 'ok', 'dispositivo': dispositivo.nombre})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    elif request.method == 'GET':
        return JsonResponse({'status': 'ok', 'message': 'API activa. Usa POST para enviar datos.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'})
