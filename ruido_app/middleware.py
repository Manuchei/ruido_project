from django.shortcuts import redirect
from django.urls import resolve

class FlujoSeleccionMiddleware:
    """
    Asegura que el usuario:
    1) Debe estar logueado para acceder a seleccionar edificio
    2) Debe haber elegido edificio para acceder a seleccionar dispositivo
    3) Debe haber elegido dispositivo para ver mediciones
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        
        protected_paths = [
            "seleccionar_edificio",
            "seleccionar_dispositivo",
            "ver_dispositivo",
        ]

        current_url = resolve(request.path_info).url_name

        # Si la URL no tiene nombre (admin, login, static...) permitimos
        if not current_url:
            return self.get_response(request)

        # 1) Si NO estás logueado → al login
        if current_url in protected_paths and not request.user.is_authenticated:
            return redirect("login")

        # 2) Si NO hay edificio seleccionado → NO permitimos acceder al dispositivo
        if current_url == "seleccionar_dispositivo" and not request.session.get("edificio_id"):
            return redirect("seleccionar_edificio")

        # 3) Si NO hay edificio → NO permitimos ver un dispositivo
        if current_url == "ver_dispositivo" and not request.session.get("edificio_id"):
            return redirect("seleccionar_edificio")

        return self.get_response(request)
