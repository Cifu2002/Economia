from django.db import models

# Create your models here.
from django.db import models

from django.core.exceptions import ValidationError

TIPOS_CREDITO = {
    "Productivo Corporativo": 10.49,
    "Productivo Empresarial": 13.22,
    "Productivo PYMES": 12.13,
    "Consumo": 16.77,
    "Educativo": 9.50,
    "Educativo Social": 7.50,
    "Vivienda de Interés Público": 4.99,
    "Vivienda de Interés Social": 4.99,
    "Inmobiliario": 11.51,
    "Microcrédito Minorista": 28.23,
    "Microcrédito de Acumulación Simple": 24.89,
    "Microcrédito de Acumulación Ampliada": 22.05,
    "Inversión Pública": 9.33,
}

TIPO_CHOICES = [(key, key) for key in TIPOS_CREDITO.keys()]

class TipoCredito(models.Model):
    tipo = models.CharField(max_length=50, choices=TIPO_CHOICES)
    nombre = models.CharField(max_length=100)
    interes_anual = models.DecimalField(max_digits=5, decimal_places=2)
    seguro = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        max_tasa = TIPOS_CREDITO.get(self.tipo)
        if self.interes_anual > max_tasa:
            raise ValidationError({
                'interes_anual': f"La tasa máxima para el tipo '{self.tipo}' es {max_tasa}%. No puede ser mayor."
            })

        if self.seguro > 25:
            raise ValidationError({
                'seguro': "El seguro no puede ser mayor al 25%."
            })

    def __str__(self):
        return self.nombre


class Simulacion(models.Model):
    tipo_credito = models.ForeignKey('TipoCredito', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    plazo_meses = models.PositiveIntegerField()
    metodo_pago = models.CharField(max_length=20, choices=[('FRANCES', 'Francés'), ('ALEMAN', 'Alemán')])

    cuota = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cuota_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_pagar = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tipo_credito.nombre} - {self.monto} USD"