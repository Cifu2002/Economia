from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib import messages
from django.template.loader import render_to_string
from decimal import Decimal, getcontext
from .forms import SimulacionForm
from .models import Simulacion, TipoCredito
from .utils import generar_pdf_simulacion, generar_pdf_simulacion_desde_datos
from django.views.decorators.http import require_GET
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

getcontext().prec = 10

# Vista principal del formulario
def simular_credito(request):
    resultado = None
    """ Diccionario de amortizacion """
    tabla_amortizacion = []
    if request.method == 'POST':
        form = SimulacionForm(request.POST)
        if form.is_valid():
            simulacion = form.save(commit=False)
            monto = simulacion.monto
            plazo = simulacion.plazo_meses
            interes_efectivo_anual = Decimal(simulacion.tipo_credito.interes_anual)
            tasa_efectiva = interes_efectivo_anual / Decimal(100)
            tasa_mensual = (Decimal(1) + tasa_efectiva) ** (Decimal(1) / Decimal(12)) - Decimal(1)
            interes_anual = (tasa_mensual * Decimal(12)) * 100
            interes_anual = interes_anual.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            interes_mensual = Decimal(interes_anual) / Decimal(12) / Decimal(100)
            seguro = Decimal(simulacion.tipo_credito.seguro) / Decimal(100) 
            total_seguro = Decimal('0.00')
            saldo = monto
            primer_seguro=0
            es_primer_mes = True
            """ Otras opciones """
            solca = form.cleaned_data.get('solca') or 0
            tipo_solca = form.cleaned_data.get('tipo_solca')
            donacion = form.cleaned_data.get('donacion') or 0
            tipo_donacion = form.cleaned_data.get('tipo_donacion')
            seguro_desgravamen = form.cleaned_data.get('seguro_desgravamen')
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
            """ Si tiene seguro desgravamen """
            """ if seguro_desgravamen:
                if simulacion.metodo_pago == 'FRANCES':
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

                elif simulacion.metodo_pago == 'ALEMAN':
                    amortizacion = monto / plazo
                    total_seguro = Decimal(0)
                    total_pagar = Decimal(0)
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
            # Si NO incluye seguro de desgravamen
            else:
                if simulacion.metodo_pago == 'FRANCES':
                    if interes_mensual == 0:
                        cuota = monto / plazo
                    else:
                        cuota = monto * (interes_mensual * (1 + interes_mensual) ** plazo) / ((1 + interes_mensual) ** plazo - 1)
                    total_pagar = cuota * plazo

                elif simulacion.metodo_pago == 'ALEMAN':
                    amortizacion = monto / plazo
                    total_pagar = Decimal(0)
                    saldo = monto
                    for _ in range(plazo):
                        interes_mes = saldo * interes_mensual
                        cuota = amortizacion + interes_mes
                        total_pagar += cuota
                        saldo -= amortizacion """

            if seguro_desgravamen:
                if simulacion.metodo_pago == 'FRANCES':
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

                elif simulacion.metodo_pago == 'ALEMAN':
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
                if simulacion.metodo_pago == 'FRANCES':
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

                elif simulacion.metodo_pago == 'ALEMAN':
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
            

            simulacion.save()
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
    else:
        form = SimulacionForm()

    return render(request, 'main/home.html', {
        'form': form,
        'resultado': resultado,
    })


# Vista para generar PDF de simulación
""" def generar_pdf(request, simulacion_id):
    simulacion = get_object_or_404(Simulacion, id=simulacion_id)
    return generar_pdf_simulacion(simulacion, request)
 """
# Vista para generar PDF de simulación
def generar_pdf(request, simulacion_id):
    simulacion = get_object_or_404(Simulacion, id=simulacion_id)

    try:
        solca = Decimal(request.GET.get('solca', '0').replace(',', '.'))
    except (InvalidOperation, TypeError):
        solca = Decimal('0')

    tipo_solca = request.GET.get('tipo_solca')
    
    try:
        donacion = Decimal(request.GET.get('donacion', '0').replace(',', '.'))
    except (InvalidOperation, TypeError):
        donacion = Decimal('0')


    tipo_donacion = request.GET.get('tipo_donacion')

    seguro_desgravamen = request.GET.get('seguro_desgravamen') == '1'

    return generar_pdf_simulacion(
        simulacion,
        request=request,
        solca=solca,
        tipo_solca=tipo_solca,  
        donacion=donacion,
        tipo_donacion=tipo_donacion,  
        seguro_desgravamen=seguro_desgravamen
    )

# ✅ Vista para simular desde el admin sin guardar una simulación
@require_GET
def ejecutar_simulacion_view(request, id):
    tipo_credito = get_object_or_404(TipoCredito, pk=id)

    # Parámetros enviados por GET
    try:
        monto = Decimal(request.GET.get('monto', '1000'))
        plazo = int(request.GET.get('plazo', '12'))
        metodo_pago = request.GET.get('metodo', 'FRANCES').upper()
    except (ValueError, TypeError, Decimal.InvalidOperation):
        return JsonResponse({'error': 'Parámetros inválidos'}, status=400)

    interes_mensual = Decimal(tipo_credito.interes_anual) / Decimal(12) / Decimal(100)
    seguro = tipo_credito.seguro

    if metodo_pago == 'FRANCES':
        if interes_mensual == 0:
            cuota = monto / plazo
        else:
            cuota = monto * (interes_mensual * (1 + interes_mensual) ** plazo) / ((1 + interes_mensual) ** plazo - 1)
    elif metodo_pago == 'ALEMAN':
        amortizacion = monto / plazo
        cuota = amortizacion + (monto * interes_mensual)
    else:
        return JsonResponse({'error': 'Método de pago inválido'}, status=400)

    cuota_total = cuota + seguro
    total_pagar = cuota_total * plazo

    return JsonResponse({
        'monto': round(monto, 2),
        'plazo': plazo,
        'interes_anual': float(tipo_credito.interes_anual),
        'seguro': float(seguro),
        'metodo_pago': metodo_pago,
        'cuota': round(cuota, 2),
        'cuota_total': round(cuota_total, 2),
        'total_pagar': round(total_pagar, 2),
    })
def simulador_view(request, pk):
    tipo_credito = get_object_or_404(TipoCredito, pk=pk)
    # lógica del simulador aquí
    return render(request, 'main/simulador.html', {'tipo_credito': tipo_credito})




def generar_pdf_dinamico(request):
    tabla = []
    # Parámetros enviados por GET
    try:
        monto = Decimal(request.GET.get('monto', '1000').replace(',', '.'))
        plazo = int(request.GET.get('plazo', '12'))
        metodo_pago = request.GET.get('metodo')
        tipo_credito_nombre = request.GET.get('tipo_credito', 'Simulación')  # Valor por defecto
        
        try:
            interes_efectivo_anual = Decimal(request.GET.get('interes_efectivo_anual', '0').replace(',', '.'))
        except (InvalidOperation, TypeError):
            interes_efectivo_anual = Decimal('0')

        try:
            seguro = Decimal(request.GET.get('seguro', '0').replace(',', '.'))
        except (InvalidOperation, TypeError):
            seguro = Decimal('0')

        try:
            donacion = Decimal(request.GET.get('donacion', '0').replace(',', '.'))
        except (InvalidOperation, TypeError):
            donacion = Decimal('0')

        try:
            solca = Decimal(request.GET.get('solca', '0').replace(',', '.'))
        except (InvalidOperation, TypeError):
            solca = Decimal('0')

        tipo_donacion = request.GET.get('tipo_donacion') or None
        tipo_solca = request.GET.get('tipo_solca') or None

        seguro_desgravamen = request.GET.get('seguro_desgravamen', '0').lower() in ['1', 'true', 'on']


    except (ValueError, TypeError) as e:
        return JsonResponse({'error': f'Parámetros inválidos: {str(e)}'}, status=400)

    
            
            
    tasa_efectiva = interes_efectivo_anual / Decimal(100)
    tasa_mensual = (Decimal(1) + tasa_efectiva) ** (Decimal(1) / Decimal(12)) - Decimal(1)
    interes_anual = (tasa_mensual * Decimal(12)) * 100
    interes_anual = interes_anual.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    interes_mensual = Decimal(interes_anual) / Decimal(12) / Decimal(100)      
    total_seguro = Decimal('0.00')
    saldo = monto
    primer_seguro=0
    es_primer_mes = True
            
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
    """ Si tiene seguro desgravamen """
    if seguro_desgravamen:
        if metodo_pago == 'FRANCES':
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

                tabla.append({
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

        elif metodo_pago == 'ALEMAN':
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

                tabla.append({
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
        if metodo_pago == 'FRANCES':
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

                tabla.append({
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

        elif metodo_pago == 'ALEMAN':
            amortizacion = monto / plazo
            saldo = monto
            total_pagar = Decimal(0)

            for mes in range(1, plazo + 1):
                interes_mes = saldo * interes_mensual
                cuota = amortizacion + interes_mes
                saldo -= amortizacion
                cuota_total = cuota + donacion_mensual + solca_mensual
                total_pagar += cuota

                tabla.append({
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
    datos_simulacion = {
        'cuota': round(cuota, 2),
        'cuota_total': round(cuota + primer_seguro + donacion_mensual + solca_mensual, 2),
        'seguro_total': round(total_seguro, 2),
        'total_pagar': round(total_pagar, 2),
        'plazo': plazo,
        'interes_efectivo': interes_efectivo_anual,
        'interes': interes_anual,
        'solca': solca,
        'solca_dinero': round(monto * (Decimal(solca) / 100), 2),
        'donacion_dinero': round(monto * (Decimal(donacion) / 100), 2),
        'tipo_solca': tipo_solca,
        'donacion': donacion,
        'tipo_donacion': tipo_donacion,
        'seguro_desgravamen': seguro_desgravamen,
        'donacion_mensual': donacion_mensual,
        'solca_mensual': solca_mensual,
        'tabla': tabla,
        'tipo_credito': tipo_credito_nombre,
        'seguro':seguro,
        'monto':monto,
        'metodo':metodo_pago,
    }

    return generar_pdf_simulacion_desde_datos(datos_simulacion, request)