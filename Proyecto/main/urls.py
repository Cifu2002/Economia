from django.urls import path, include
from .views import ejecutar_simulacion_view


from . import views

urlpatterns = [
    path("", views.simular_credito, name='home'),
    path('simulador/pdf/<int:simulacion_id>/', views.generar_pdf, name='generar_pdf'),
    path('admin/app/simulacion/<int:id>/ejecutar_simulacion/', ejecutar_simulacion_view, name='ejecutar_simulacion'),
    path('main/<int:pk>/simulador/', views.simulador_view, name='simulador'), 
    path('simulador/pdf-temp/', views.generar_pdf_dinamico, name='generar_pdf_temp'), 
]
