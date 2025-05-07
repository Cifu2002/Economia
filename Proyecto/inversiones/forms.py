from django import forms
from .models import TIPOS_ACTIVO
from .models import ConfiguracionActivo

UNIDADES_TIEMPO = [
    ('años', 'Años'),
    ('meses', 'Meses'),
]

class SimulacionForm(forms.Form):
    monto = forms.FloatField(label="Monto a invertir", min_value=0.01, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    tipo_activo = forms.ModelChoiceField(
        queryset=ConfiguracionActivo.objects.all(),
        empty_label="Seleccione un tipo de inversión",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    plazo = forms.IntegerField(label="Plazo", min_value=1, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    unidad_tiempo = forms.ChoiceField(choices=UNIDADES_TIEMPO, widget=forms.Select(attrs={'class': 'form-control'}))
    reinvertir = forms.BooleanField(label="¿Reinvertir ganancias?", required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

