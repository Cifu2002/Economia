from django import forms
from .models import Simulacion, TipoCredito
from decimal import Decimal
from decimal import Decimal, ROUND_HALF_UP
from decimal import Decimal, getcontext
getcontext().prec = 10

class SimuladorAdminForm(forms.Form):
    monto = forms.DecimalField(label="Monto", min_value=100, decimal_places=2)
    PLAZO_MESES = [
        (6, '6 meses '),
        (12, '12 meses (1 año)'),
        (24, '24 meses (2 años)'),
        (36, '36 meses (3 años)'),
        (48, '48 meses (4 años)'),
        (60, '60 meses (5 años)'),
        (72, '72 meses (6 años)'),
        (84, '84 meses (7 años)'),
        (96, '96 meses (8 años)'),
        (108, '108 meses (9 años)'),
        (120, '120 meses (10 años)'),
    ]

    plazo_meses = forms.ChoiceField(
        choices= PLAZO_MESES,
        #widget= forms.Select(attrs={'class': 'form-control'})
        
        )
    metodo_pago = forms.ChoiceField(choices=[('FRANCES', 'Francés'), ('ALEMAN', 'Alemán')])
TIPO_DONACION_CHOICES = [
    ('monto', 'Monto'),
    ('porcentaje', 'Porcentaje'),
]

TIPO_SOLCA_CHOICES = [
    ('porcentaje', 'Porcentaje (0.5%)'),
    ('monto', 'Monto específico'),
]
class SimulacionForm(forms.ModelForm):
    PLAZO_CHOICES = [
        (3, '3 meses'),
        (4, '4 meses'),
        (5, '5 meses'),
        (6, '6 meses'),
        (7, '7 meses'),
        (8, '8 meses'),
        (9, '9 meses'),
        (10, '10 meses'),
        (11, '11 meses'),
        (12, '12 meses (1 año)'),
        (15, '15 meses (1.25 años)'),
        (18, '18 meses (1.5 años)'),
        (21, '21 meses (1.75 años)'),
        (24, '24 meses (2 años)'),
        (30, '30 meses (2.5 años)'),
        (36, '36 meses (3 años)'),
        (42, '42 meses (3.5 años)'),
        (48, '48 meses (4 años)'),
        (54, '54 meses (4.5 años)'),
        (60, '60 meses (5 años)'),
        (66, '66 meses (5.5 años)'),
        (72, '72 meses (6 años)'),
        (78, '78 meses (6.5 años)'),
        (84, '84 meses (7 años)'),
        (90, '90 meses (7.5 años)'),
        (96, '96 meses (8 años)'),
        (102, '102 meses (8.5 años)'),
        (108, '108 meses (9 años)'),
        (114, '114 meses (9.5 años)'),
        (120, '120 meses (10 años)'),
        (126, '126 meses (10.5 años)'),
        (132, '132 meses (11 años)'),
        (144, '144 meses (12 años)'),
        (150, '150 meses (12.5 años)'),
        (156, '156 meses (13 años)'),
        (168, '168 meses (14 años)'),
        (180, '180 meses (15 años)'),
    ]

    plazo_meses = forms.ChoiceField(
        choices=PLAZO_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    """ Donaciones para fundaciones"""
    donacion = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': 'any'}),
        initial=0,
        help_text="Donaciones (máximo 10% del monto del crédito)"
    )

    tipo_donacion = forms.ChoiceField(
        required=False,
        choices=[('', '---------')] + TIPO_DONACION_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    """ Segura desgravem """
    seguro_desgravamen = forms.BooleanField(
        required=False,
        initial=True, 
        label="Incluir seguro de desgravamen",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


    """ Solca """
    solca = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'step': 'any',
            'placeholder': '0.5%'
        }),
        initial=Decimal('0.5'),
        help_text="Contribución a SOLCA (máximo 0.5% del monto del crédito)"
    )

    tipo_solca = forms.ChoiceField(
        required=False,
        choices=[('', '---------')] + TIPO_SOLCA_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='---------'
    )

    class Meta:
        model = Simulacion
        fields = ['tipo_credito', 'monto', 'plazo_meses', 'metodo_pago', 'donacion', 'tipo_donacion', 'seguro_desgravamen']
        widgets = {
            'tipo_credito': forms.Select(attrs={'class': 'form-control', 'id': 'tipoCreditoSelect'}),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monto en $'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        opciones = [('', '---------')]
        opciones += [(tipo.id, tipo.nombre) for tipo in TipoCredito.objects.all()]
        self.fields['tipo_credito'].choices = opciones
        self.fields['tipo_credito'].widget.attrs.update({'id': 'tipoCreditoSelect'})


        
    def get_standard_fields(self):
        """Devuelve una lista de campos estándar (no adicionales)"""
        additional_fields = ['tipo_credito','donacion', 'tipo_donacion', 'seguro_desgravamen', 'solca', 'tipo_solca']
        return [field for field in self if field.name not in additional_fields]

    def get_donation_fields(self):
        """Devuelve una lista de campos adicionales"""
        additional_fields = ['seguro_desgravamen']
        return [field for field in self if field.name in additional_fields]
    
    def clean(self):
        cleaned_data = super().clean()
        monto = cleaned_data.get('monto')
        donacion = cleaned_data.get('donacion')
        tipo_donacion = cleaned_data.get('tipo_donacion')
        solca = cleaned_data.get('solca')
        tipo_solca = cleaned_data.get('tipo_solca')

        # Validación de donaciones para fundaciones
        if donacion is not None and tipo_donacion and monto is not None:
            if tipo_donacion == 'porcentaje':
                if donacion > Decimal('10'):
                    self.add_error('donacion', "No puede superar el 10% en tipo porcentaje.")
            elif tipo_donacion == 'monto':
                max_donacion = monto * Decimal('0.10')
                if donacion > max_donacion:
                    self.add_error('donacion', f"No puede superar el 10% del monto (${max_donacion:.2f}).")

        # Validación de contribución SOLCA (se mantiene en 0.5%)
        if solca is not None and tipo_solca and monto is not None:
            if tipo_solca == 'porcentaje':
                if solca > Decimal('0.5'):
                    self.add_error('solca', "No puede superar el 0.5% en tipo porcentaje.")
            elif tipo_solca == 'monto':
                max_solca = monto * Decimal('0.005')
                if solca > max_solca:
                    self.add_error('solca', f"No puede superar el 0.5% del monto (${max_solca:.2f}).")
        
        # Validación para SOLCA
        if solca is not None and tipo_solca and monto is not None:
            if tipo_solca == 'porcentaje':
                # Si es porcentaje, forzamos a que sea 0.5%
                if solca != Decimal('0.5'):
                    cleaned_data['solca'] = Decimal('0.5')
            elif tipo_solca == 'monto':
                max_solca = monto * Decimal('0.005')
                if solca > max_solca:
                    self.add_error('solca', f"No puede superar el 0.5% del monto (${max_solca:.2f}).")
        
        return cleaned_data

    def clean_plazo_meses(self):
        plazo = int(self.cleaned_data['plazo_meses'])
        if plazo <= 0 or plazo > 360:
            raise forms.ValidationError("El plazo debe estar entre 1 y 360 meses.")
        return plazo

    """ def calcular_simulacion(self):
        tipo = self.cleaned_data['tipo_credito']
        monto = self.cleaned_data['monto']
        plazo = int(self.cleaned_data['plazo_meses'])
        metodo = self.cleaned_data['metodo_pago']

        interes_anual = tipo.interes_anual
        interes_mensual = Decimal(interes_anual) / Decimal(12) / Decimal(100)
        seguro = tipo.seguro

        cuota_sin_seguro = 0

        if metodo == 'FRANCES':
            if interes_mensual == 0:
                cuota_sin_seguro = monto / plazo
            else:
                cuota_sin_seguro = monto * (interes_mensual * (1 + interes_mensual) ** plazo) / ((1 + interes_mensual) ** plazo - 1)
        elif metodo == 'ALEMAN':
            amortizacion = monto / plazo
            cuota_sin_seguro = amortizacion + (monto * interes_mensual)

        cuota_total = cuota_sin_seguro + seguro
        total_pagar = cuota_total * plazo

        return {
            'cuota': round(cuota_sin_seguro, 2),
            'seguro': round(seguro, 2),
            'cuota_total': round(cuota_total, 2),
            'plazo': plazo,
            'interes': interes_anual,
            'total_pagar': round(total_pagar, 2),
        }
 """
    """ def calcular_simulacion(self):
        tipo = self.cleaned_data['tipo_credito']
        monto = self.cleaned_data['monto']
        plazo = int(self.cleaned_data['plazo_meses'])
        interes_efectivo_anual = Decimal(tipo.interes_anual)
        tasa_efectiva = interes_efectivo_anual / Decimal(100)
        tasa_mensual = (Decimal(1) + tasa_efectiva) ** (Decimal(1) / Decimal(12)) - Decimal(1)
        interes_anual = (tasa_mensual * Decimal(12)) * 100
        interes_anual = interes_anual.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        interes_mensual = Decimal(interes_anual) / Decimal(12) / Decimal(100)
        seguro = Decimal(tipo.seguro) / Decimal(100) 
        total_seguro = Decimal('0.00')
        saldo = monto
        primer_seguro=0
        es_primer_mes = True
        metodo = self.cleaned_data['metodo_pago']

        if metodo == 'FRANCES':
            if interes_mensual == 0:
                cuota = monto / plazo
            else:
                cuota = monto * (interes_mensual * (1 + interes_mensual) ** plazo) / ((1 + interes_mensual) ** plazo - 1)
            for _ in range(plazo):
                interes_mes = saldo * interes_mensual
                capital_mes = cuota - interes_mes
                seguro_mes = saldo * seguro
                if es_primer_mes:
                    primer_seguro = seguro_mes
                    es_primer_mes = False
                total_seguro += seguro_mes
                saldo -= capital_mes
            total_pagar = (cuota * plazo) + total_seguro

        elif metodo == 'ALEMAN':
            amortizacion = monto / plazo
            total_pagar = Decimal(0)
            total_seguro = Decimal(0)
            saldo = monto  
            for _ in range(plazo):
                interes_mes = saldo * interes_mensual
                cuota = amortizacion + interes_mes
                seguro_mes = saldo * seguro

                total_pagar += cuota
                if es_primer_mes:
                    primer_seguro = seguro_mes
                    es_primer_mes = False
                total_seguro += seguro_mes
                saldo -= amortizacion

            total_pagar += total_seguro

        return {
            'cuota': round(cuota, 2),
            'cuota_total': round(cuota+primer_seguro, 2),
            'seguro_total': round(total_seguro, 2),
            'total_pagar': round(total_pagar, 2),
            'seguro': round(seguro, 2),
            'plazo': plazo,
            'interes_efectivo': interes_efectivo_anual,
            'interes': interes_anual,
        } """

        
