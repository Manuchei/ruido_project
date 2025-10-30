from django.shortcuts import render
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import LecturaRuido
import json

# Create your views here.

# Página principal
def home(request):
    lecturas = LecturaRuido.objects.order_by('-fecha_hora')[:10] # últimas 10 lecturas
    return render(request, 'index.html', {'lecturas': lecturas})

# API para recibir datos desde Arduino
@csrf_exempt
def recibir_ruido(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            nivel = float(data.get('nivel_db'))
            lectura = LecturaRuido.objects.create(nivel_db=nivel)
            return JsonResponse({'status': 'ok', 'id': lectura.id})
        except Exception as e:
            return JsonResponse({'status': 'ok', 'message': str(e)})
    elif request.method == 'GET':
        #Respuesta simple si accedes desde navegador
        return JsonResponse({'status': 'ok', 'message': 'La API está activa. Usa POST para enviar datos.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'})