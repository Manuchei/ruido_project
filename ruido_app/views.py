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

    # 🟦 ADMIN → puede ver todo
    if request.user.is_superuser:
        edificios = Edificio.objects.all()

    # 🟩 USUARIO NORMAL → solo su edificio
    else:
        edificio_user = getattr(request.user, "edificio", None)
        if edificio_user:
            edificios = [edificio_user]  # lista con 1 edificio
        else:
            edificios = []  # por si algún usuario no tiene edificio

    if request.method == "POST":
        edificio_id = request.POST.get("edificio_id")

        # 🚫 Seguridad: usuario normal NO puede elegir otro edificio
        if not request.user.is_superuser:
            if str(request.user.edificio.id) != edificio_id:
                return render(request, "error.html", {
                    "mensaje": "No tienes permiso para seleccionar este edificio."
                })

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

    # ✔ USUARIO NORMAL: prohibir acceder a edificios que no son suyos
    if not request.user.is_superuser:
        if edificio != request.user.edificio:
            return render(request, "error.html", {
                "mensaje": "No tienes permiso para acceder a este edificio."
            })

    dispositivos = edificio.dispositivos.all()

    return render(request, "seleccionar_dispositivo.html", {
        "dispositivos": dispositivos
    })


# ----------------------------
#   API POST de dispositivos
# ----------------------------
@csrf_exempt
def recibir_ruido(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))

            # Datos que envía Arduino
            nivel = float(data.get("nivel_db"))
            api_key = data.get("api_key")
            rms = data.get("rms", None)

            presencia_raw = data.get("presencia", 0)
            presencia = bool(int(presencia_raw)) if isinstance(presencia_raw, (int, str)) else bool(presencia_raw)

            # Buscar dispositivo por API key
            dispositivo = Dispositivo.objects.filter(api_key=api_key).first()
            if not dispositivo:
                return JsonResponse({
                    "status": "error",
                    "mensaje": "Dispositivo no encontrado"
                }, status=400)

            # Guardar lectura
            LecturaRuido.objects.create(
                dispositivo=dispositivo,
                nivel_db=nivel,
                presencia=presencia
                # Si tienes rms en modelo → añade: rms=rms
            )

            # Limpieza automática 24h
            limite = timezone.now() - timedelta(hours=24)
            LecturaRuido.objects.filter(fecha_hora__lt=limite).delete()

            return JsonResponse({
                "status": "ok",
                "dispositivo": dispositivo.nombre,
                "nivel_db": nivel,
                "rms": rms,
                "presencia": presencia
            })

        except Exception as e:
            return JsonResponse({
                "status": "error",
                "mensaje": str(e)
            })

    # 🔵 Modo navegador GET
    elif request.method == "GET":
        ultima = LecturaRuido.objects.last()

        if ultima:
            return JsonResponse({
                "status": "ok",
                "ultimo_ruido": {
                    "dispositivo": ultima.dispositivo.nombre,
                    "nivel_db": ultima.nivel_db,
                    "presencia": ultima.presencia,
                    "fecha": ultima.fecha_hora.strftime("%d/%m/%Y %H:%M:%S")
                    # Si tienes rms en modelo, añade: "rms": ultima.rms
                }
            })

        return JsonResponse({
            "status": "ok",
            "mensaje": "API activa, todavía sin datos"
        })

@login_required
def ver_dispositivo(request, id):

    dispositivo = Dispositivo.objects.filter(id=id).first()
    if not dispositivo:
        return render(request, "error.html", {"mensaje": "El dispositivo no existe"})

    # ✔ USUARIO NORMAL: solo su edificio
    if not request.user.is_superuser:
        if dispositivo.edificio != request.user.edificio:
            return render(request, "error.html", {"mensaje": "No tienes permiso para ver este dispositivo"})

    lecturas = dispositivo.lecturas.order_by('-fecha_hora')[:50]

    return render(request, "index.html", {
        "dispositivo": dispositivo,
        "lecturas": lecturas
    })
