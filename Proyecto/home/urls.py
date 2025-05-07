from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='index'),
    path('cuentas/',views.cuentas, name='cuentas'),
    path('terminos/',views.terminos, name='terminos'),
    path('nuevo/',views.nuevo, name='nuevo'),
    
]