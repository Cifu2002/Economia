from django.urls import path

from . import views

urlpatterns = [
    path('', views.inversiones, name='inversiones'),
    path('generar-pdf/', views.generar_pdf, name='generar_pdf'),

    
]