from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
from django.urls import reverse

from .models import TipoCredito, Simulacion

# Personalización del panel de administración
admin.site.site_header = "Panel de Administración"
admin.site.site_title = "Administración del Sitio"
admin.site.index_title = "Panel de control"


# Formulario personalizado para la vista del simulador
class SimuladorAdminForm(forms.Form):
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

    monto = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=True, 
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Monto del crédito'}))

    plazo_meses = forms.ChoiceField(
        choices=[('', '---------')] + PLAZO_CHOICES,  
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select py-2',
            'style': 'min-height: 48px;'
        })
    )
    
    # Restablecer los widgets de los selectores para mostrar correctamente en la vista
    metodo_pago = forms.ChoiceField(
        choices=[('', '---------'),('FRANCES', 'Frances'), ('ALEMAN', 'Aleman')],
        required=True,
        widget=forms.Select(attrs={
            'class': 'form-select py-2',
            'style': 'min-height: 48px;'
        })
    )

    tipo_donacion = forms.ChoiceField(
        choices=[('', '---------'),('monto', 'Monto'), ('porcentaje', 'Porcentaje')],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select py-2',
            'style': 'min-height: 48px;'
        })
    )
    
    donacion = forms.DecimalField(
        max_digits=10, decimal_places=2, 
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Donaciones (máximo 10% del monto del crédito)")
    
    tipo_solca = forms.ChoiceField(
        choices=[
            ('', '---------'),
            ('porcentaje', 'Porcentaje (0,5%)'),
            ('monto', 'Monto')
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select py-2',
            'style': 'min-height: 48px;'
        })
    )
    
    solca = forms.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False, 
        widget=forms.NumberInput(attrs={'class': 'form-control'}),
        help_text="Contribución a SOLCA (máximo 0.5% del monto del crédito)")
    
    seguro_desgravamen = forms.BooleanField(
    required=False,
    initial=True,
    widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
)



@admin.register(TipoCredito)
class TipoCreditoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'interes_anual', 'seguro', 'simular_credito')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:tipo_credito_id>/simulador/',
                self.admin_site.admin_view(self.simulador_view),
                name='simulador_credito'
            ),
        ]
        return custom_urls + urls

    def simular_credito(self, obj):
        url = reverse('admin:simulador_credito', args=[obj.id])
        return format_html(
            '<a class="button" href="{}">Simular</a>',
            url
        )
    simular_credito.short_description = 'Simulación'
    simular_credito.allow_tags = True

    def simulador_view(self, request, tipo_credito_id):
        tipo_credito = get_object_or_404(TipoCredito, pk=tipo_credito_id)
        resultado = None
        tabla_amortizacion = []

        if request.method == 'POST':
            form = SimuladorAdminForm(request.POST)
            if form.is_valid():
                monto = form.cleaned_data['monto']
                plazo = int(form.cleaned_data['plazo_meses'])
                metodo = form.cleaned_data['metodo_pago']
                interes_efectivo_anual = Decimal(tipo_credito.interes_anual)
                tasa_efectiva = interes_efectivo_anual / Decimal(100)
                tasa_mensual = (Decimal(1) + tasa_efectiva) ** (Decimal(1) / Decimal(12)) - Decimal(1)
                interes_anual = (tasa_mensual * Decimal(12)) * 100
                interes_anual = interes_anual.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                interes_mensual = Decimal(interes_anual) / Decimal(12) / Decimal(100)
                seguro = Decimal(tipo_credito.seguro) / Decimal(100) 
                total_seguro = Decimal('0.00')
                saldo = monto
                primer_seguro=0
                es_primer_mes = True
                """ Otras opciones """
                tipo_donacion      = form.cleaned_data['tipo_donacion']
                donacion           = form.cleaned_data['donacion'] or Decimal('0')
                tipo_solca         = form.cleaned_data['tipo_solca']
                solca              = form.cleaned_data['solca'] or Decimal('0')
                seguro_desgravamen = form.cleaned_data['seguro_desgravamen'] 
                """ Varibles de acumulacion """
                total_seguro = Decimal(0)
                total_pagar = Decimal(0)
                saldo = monto
                es_primer_mes = True
                primer_seguro = Decimal(0)
                donacion_mensual = Decimal(0)
                solca_mensual = Decimal(0)
                
                if tipo_donacion == 'monto':
                    donacion_mensual = donacion / plazo

                if tipo_solca == 'monto':
                    solca_mensual = solca / plazo

                if seguro_desgravamen:
                    if metodo == 'FRANCES':
                        if interes_mensual == 0:
                            cuota = monto / plazo
                        else:
                            cuota = monto * (interes_mensual * (1 + interes_mensual) ** plazo) / ((1 + interes_mensual) ** plazo - 1)
                        for mes in range(1, plazo + 1):
                            interes_mes = saldo * interes_mensual
                            capital_mes = cuota - interes_mes
                            seguro_mes = saldo * seguro if seguro_desgravamen else 0
                            if es_primer_mes:
                                primer_seguro = seguro_mes
                                es_primer_mes = False
                            total_seguro += seguro_mes
                            saldo -= capital_mes
                            cuota_total = cuota + seguro_mes + donacion_mensual + solca_mensual

                            tabla_amortizacion.append({
                                'mes': mes,
                                'saldo': round(saldo, 2),
                                'cuota': round(cuota, 2),
                                'capital': round(capital_mes, 2),
                                'interes': round(interes_mes, 2),
                                'seguro': round(seguro_mes, 2),
                                'solca': round(solca_mensual, 2),
                                'donacion': round(donacion_mensual, 2),
                                'cuota_total': round(cuota_total, 2),
                            })

                        total_pagar = (cuota * plazo) + total_seguro

                    elif metodo == 'ALEMAN':
                        amortizacion = monto / plazo
                        for mes in range(1, plazo + 1):
                            interes_mes = saldo * interes_mensual
                            cuota = amortizacion + interes_mes
                            seguro_mes = saldo * seguro if seguro_desgravamen else 0
                            if es_primer_mes:
                                primer_seguro = seguro_mes
                                es_primer_mes = False
                            total_seguro += seguro_mes
                            saldo -= amortizacion
                            cuota_total = cuota + seguro_mes + donacion_mensual + solca_mensual
                            total_pagar += cuota

                            tabla_amortizacion.append({
                                'mes': mes,
                                'saldo': round(saldo, 2),
                                'cuota': round(cuota, 2),
                                'capital': round(amortizacion, 2),
                                'interes': round(interes_mes, 2),
                                'seguro': round(seguro_mes, 2),
                                'solca': round(solca_mensual, 2),
                                'donacion': round(donacion_mensual, 2),
                                'cuota_total': round(cuota_total, 2),
                            })

                        total_pagar += total_seguro
                # Si NO incluye seguro de desgravamen
                else:
                    if metodo == 'FRANCES':
                        if interes_mensual == 0:
                            cuota = monto / plazo
                        else:
                            cuota = monto * (interes_mensual * (1 + interes_mensual) ** plazo) / ((1 + interes_mensual) ** plazo - 1)

                        saldo = monto
                        for mes in range(1, plazo + 1):
                            interes_mes = saldo * interes_mensual
                            capital_mes = cuota - interes_mes
                            saldo -= capital_mes
                            cuota_total = cuota + donacion_mensual + solca_mensual

                            tabla_amortizacion.append({
                                'mes': mes,
                                'saldo': round(saldo, 2),
                                'cuota': round(cuota, 2),
                                'capital': round(capital_mes, 2),
                                'interes': round(interes_mes, 2),
                                'seguro': Decimal('0.00'),
                                'solca': round(solca_mensual, 2),
                                'donacion': round(donacion_mensual, 2),
                                'cuota_total': round(cuota_total, 2),
                            })

                        total_pagar = cuota * plazo

                    elif metodo == 'ALEMAN':
                        amortizacion = monto / plazo
                        saldo = monto
                        total_pagar = Decimal(0)

                        for mes in range(1, plazo + 1):
                            interes_mes = saldo * interes_mensual
                            cuota = amortizacion + interes_mes
                            saldo -= amortizacion
                            cuota_total = cuota + donacion_mensual + solca_mensual
                            total_pagar += cuota

                            tabla_amortizacion.append({
                                'mes': mes,
                                'saldo': round(saldo, 2),
                                'cuota': round(cuota, 2),
                                'capital': round(amortizacion, 2),
                                'interes': round(interes_mes, 2),
                                'seguro': Decimal('0.00'),
                                'solca': round(solca_mensual, 2),
                                'donacion': round(donacion_mensual, 2),
                                'cuota_total': round(cuota_total, 2),
                            })
                

                """ resultado = Simulacion(
                    tipo_credito=tipo_credito,
                    monto=monto,
                    plazo_meses=plazo,
                    metodo_pago=metodo,
                    cuota=round(cuota, 2),
                    cuota_total=round(cuota_total, 2),
                    total_pagar=round(total_pagar, 2),
                ) """
                simulacion = Simulacion.objects.create(
                    tipo_credito=tipo_credito,
                    monto=monto,
                    plazo_meses=plazo,
                    metodo_pago=metodo,
                    cuota=round(cuota, 2),
                    cuota_total=round(cuota_total, 2),
                    total_pagar=round(total_pagar, 2),
                )

                resultado = {
                    'cuota': round(cuota, 2),
                    'cuota_total': round(cuota + primer_seguro + donacion_mensual + solca_mensual, 2),
                    'seguro_total': round(total_seguro, 2),
                    'total_pagar': round(total_pagar, 2),
                    'plazo': plazo,
                    'interes_efectivo': interes_efectivo_anual,
                    'interes': interes_anual,
                    'simulacion_id': simulacion.id,
                    'solca': solca,
                    'solca_dinero': round(monto * (Decimal(solca) / 100), 2),
                    'donacion_dinero': round(monto * (Decimal(donacion) / 100), 2),
                    'tipo_solca': tipo_solca,
                    'donacion': donacion,
                    'tipo_donacion': tipo_donacion,
                    'seguro_desgravamen': seguro_desgravamen,
                    'donacion_mensual': donacion_mensual,
                    'solca_mensual': solca_mensual,
                    'tabla': tabla_amortizacion,
                }


                pdf_url = reverse('main:generar_pdf_temp') + f'?monto={monto}&plazo={plazo}&metodo={metodo}&interes_efectivo_anual={interes_efectivo_anual}&seguro={seguro}&tipo_donacion={tipo_donacion}&donacion={donacion}&tipo_solca={tipo_solca}&solca={solca}&seguro_desgravamen={seguro_desgravamen}'

        else:
            form = SimuladorAdminForm()
            pdf_url = None

        context = dict(
            self.admin_site.each_context(request),
            form=form,
            resultado=resultado,
            tipo_credito=tipo_credito,
            pdf_url=pdf_url,
        )
        return TemplateResponse(request, "main/simulador_credito.html", context)

    class Media:
        js = ('admin/js/simulador.js',)
