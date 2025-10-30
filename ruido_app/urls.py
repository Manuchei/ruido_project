from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/ruido/', views.recibir_ruido, name='recibir_ruido'),
]