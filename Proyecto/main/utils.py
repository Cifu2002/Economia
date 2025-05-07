from decimal import Decimal
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.template.loader import get_template
from io import BytesIO
from types import SimpleNamespace
from decimal import Decimal
from decimal import Decimal, ROUND_HALF_UP
from .forms import SimulacionForm

def generar_tabla(monto, interes, plazo, seguro, metodo):
    tabla = []
    saldo = monto

    if metodo == 'FRANCES':
        if interes == 0:
            cuota = monto / plazo
        else:
            cuota = monto * (interes * (1 + interes) ** plazo) / ((1 + interes) ** plazo - 1)

        for mes in range(1, plazo + 1):
            interes_mensual = saldo * interes
            amortizacion = cuota - interes_mensual
            saldo -= amortizacion
            tabla.append({
                'mes': mes,
                'cuota': round(cuota + seguro, 2),
                'interes': round(interes_mensual, 2),
                'amortizacion': round(amortizacion, 2),
                'seguro': round(seguro, 2),
                'saldo': round(saldo, 2),
            })

    elif metodo == 'ALEMAN':
        amortizacion = monto / plazo
        for mes in range(1, plazo + 1):
            interes_mensual = saldo * interes
            cuota = amortizacion + interes_mensual
            saldo -= amortizacion
            tabla.append({
                'mes': mes,
                'cuota': round(cuota + seguro, 2),
                'interes': round(interes_mensual, 2),
                'amortizacion': round(amortizacion, 2),
                'seguro': round(seguro, 2),
                'saldo': round(saldo, 2),
            })

    return tabla
def generar_pdf_simulacion(simulacion, request=None,
                            solca=0, tipo_solca=None,
                            donacion=0, tipo_donacion=None,
                            seguro_desgravamen=False):
    tabla = []
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

    context = {
        'simulacion': simulacion,
        'tabla': tabla,
        'simulacion': simulacion,
        'tabla': tabla,
        'seguro_desgravamen':seguro_desgravamen,
        'donacion_mensual':donacion_mensual,
        'solca_mensual':solca_mensual,
        'donacion':donacion,
        'solca':solca,
        'tipo_donacion':tipo_donacion,
        'tipo_solca':tipo_solca,
        'interes_anual':interes_anual,
        'solca_dinero': round(monto * (solca / 100), 2),
        'donacion_dinero': round(monto * (donacion / 100), 2),
        'seguro_total':round(total_seguro, 2),
    }
    html = render_to_string('pdf/amortizacion.html', context=context, request=request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="tabla_{simulacion.id}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error al generar el PDF", status=500)

    return response

def generar_pdf_simulacion_desde_datos(simulacion_dict, request=None):
    tipo_credito_data = {
        "nombre": simulacion_dict["tipo_credito"],
        "interes_anual": Decimal(simulacion_dict["interes"]),
        "seguro": Decimal(simulacion_dict["seguro"])
    }

    simulacion_obj = SimpleNamespace(
        monto=Decimal(simulacion_dict["monto"]),
        plazo_meses=int(simulacion_dict["plazo"]),
        metodo_pago=simulacion_dict["metodo"],
        tipo_credito=SimpleNamespace(**tipo_credito_data)
    )

    interes_mensual = simulacion_obj.tipo_credito.interes_anual / Decimal(12) / Decimal(100)

   
    tabla = generar_tabla(
        monto=simulacion_obj.monto,
        interes=interes_mensual,
        plazo=simulacion_obj.plazo_meses,
        seguro=simulacion_obj.tipo_credito.seguro,
        metodo=simulacion_obj.metodo_pago
    )

    context = {
        'datos_simulacion': simulacion_dict,
        'site_logo': None,
        'site_name': "NombreBanco"
    }

    # Renderizar el HTML desde la plantilla
    template = get_template('pdf/pdf_simulacion.html')
    html = template.render(context, request=request)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="simulacion.pdf"'

    # Generar el PDF con xhtml2pdf
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse("Error al generar el PDF", status=500)

    return response