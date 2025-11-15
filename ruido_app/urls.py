from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('seleccionar_edificio/', views.seleccionar_edificio, name='seleccionar_edificio'),
    path('seleccionar_dispositivo/', views.seleccionar_dispositivo, name='seleccionar_dispositivo'),

    path('dispositivo/<int:id>/', views.ver_dispositivo, name='ver_dispositivo'),

    path('api/ruido/', views.recibir_ruido, name='recibir_ruido'),
]
