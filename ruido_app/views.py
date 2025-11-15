from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from .models import LecturaRuido, Dispositivo, Edificio
import json


# ----------------------------
#   PÁGINA PRINCIPAL (después del login)
# ----------------------------
@login_required
def home(request):
    # Si es admin → ver TODO
    if request.user.is_superuser:
        lecturas = LecturaRuido.objects.order_by('-fecha_hora')[:50]

    else:
        # Si es usuario de un edificio → solo sus dispositivos
        edificio = getattr(request.user, 'edificio', None)

        if not edificio:
            lecturas = []
        else:
            lecturas = LecturaRuido.objects.filter(
                dispositivo__edificio=edificio
            ).order_by('-fecha_hora')[:50]

    return render(request, 'index.html', {'lecturas': lecturas})


# ----------------------------
#   SELECCIONAR DISPOSITIVO
# ----------------------------
@login_required
def seleccionar_edificio(request):
    edificios = Edificio.objects.all()

    if request.method == "POST":
        edificio_id = request.POST.get("edificio_id")

        if edificio_id:
            request.session["edificio_id"] = edificio_id
            return redirect("seleccionar_dispositivo")

    return render(request, "seleccionar_edifico.html", {
        "edificios": edificios
    })
    
@login_required
def seleccionar_dispositivo(request):
    edificio_id = request.session.get("edificio_id")

    if not edificio_id:
        return redirect("seleccionar_edificio")

    edificio = Edificio.objects.get(id=edificio_id)

    dispositivos = edificio.dispositivos.all()

    return render(request, "seleccionar_dispositivo.html", {
        "dispositivos": dispositivos
    })


# ----------------------------
#   API POST de dispositivos
# ----------------------------
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

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})

@login_required
def ver_dispositivo(request, id):
    # Obtener el dispositivo
    dispositivo = Dispositivo.objects.filter(id=id).first()
    if not dispositivo:
        return render(request, "error.html", {"mensaje": "El dispositivo no existe"})

    # Evitar que un usuario acceda a dispositivos de otro edificio
    if not request.user.is_superuser:
        edificio = getattr(request.user, 'edificio', None)
        if not edificio or dispositivo.edificio != edificio:
            return render(request, "error.html", {"mensaje": "No tienes permiso para ver este dispositivo"})

    # Últimas 50 lecturas
    lecturas = dispositivo.lecturas.order_by('-fecha_hora')[:50]

    return render(request, "index.html", {
        "dispositivo": dispositivo,
        "lecturas": lecturas
    })
