from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

TIPOS_ACTIVO = [
    ('bonos', 'Bonos'),
    ('acciones', 'Acciones'),
    ('fondos', 'Fondos Mutuos'),
]

UNIDADES_TIEMPO = [
    ('años', 'Años'),
    ('meses', 'Meses'),
]

class Simulacion(models.Model):
    monto = models.FloatField()
    tipo_activo = models.CharField(max_length=100, choices=TIPOS_ACTIVO)
    plazo = models.IntegerField()
    unidad_tiempo = models.CharField(max_length=10, choices=UNIDADES_TIEMPO)
    reinvertir = models.BooleanField(default=False)

class ConfiguracionActivo(models.Model):
    tipo = models.CharField(max_length=50, choices=TIPOS_ACTIVO)
    nombre = models.CharField(max_length=100, help_text="Nombre descriptivo del tipo de inversión")
    
    rentabilidad_esperada = models.FloatField(
        help_text="En decimal, por ejemplo 0.08 para 8% anual",
        validators=[MinValueValidator(0.0), MaxValueValidator(0.5)]  # máximo 50% anual
    )
    
    volatilidad = models.FloatField(
        help_text="Desviación estándar anual en decimal",
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)]  # máximo 100% (extremadamente volátil)
    )
    
    comision = models.FloatField(
        help_text="Comisión sobre el capital total, en decimal",
        validators=[MinValueValidator(0.0), MaxValueValidator(0.2)]  # máximo 20%
    )

    def __str__(self):
        return self.nombre
