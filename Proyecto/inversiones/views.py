from django.shortcuts import render
from .forms import SimulacionForm
from .models import ConfiguracionActivo
import numpy as np
from django.template import RequestContext
import json
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.template.loader import render_to_string
def inversiones(request):
    resultado = None
    resultado_json = ""

    # Inicializamos el formulario
    form = SimulacionForm()

    if request.method == 'POST':
        form = SimulacionForm(request.POST)

        if form.is_valid():
            monto = form.cleaned_data['monto']
            tipo_activo = form.cleaned_data['tipo_activo']
            plazo = form.cleaned_data['plazo']
            unidad_tiempo = form.cleaned_data['unidad_tiempo']

            # Lógica de simulación de inversión
            try:
                rent = tipo_activo.rentabilidad_esperada
                vol = tipo_activo.volatilidad
                comision = tipo_activo.comision / 100  # comisión como decimal

                if unidad_tiempo == 'años':
                    periodos = plazo * 12
                    t = plazo
                    divisor_rent = 12
                    divisor_vol = np.sqrt(12)
                else:
                    periodos = plazo
                    t = plazo / 12
                    divisor_rent = 1
                    divisor_vol = 1

                # Aplicar comisión
                monto_inicial = monto * (1 - comision)

                # Cálculo compuesto final
                valor_final = monto_inicial * (1 + rent) ** t
                valor_min = monto_inicial * (1 + rent - vol / 100) ** t
                valor_max = monto_inicial * (1 + rent + vol / 100) ** t

                # Simular evolución mensual
                rendimiento_mensual = (1 + rent) ** (1 / 12) - 1
                capital = monto_inicial
                valores = [round(capital, 2)]
                for _ in range(int(periodos)):
                    capital += capital * rendimiento_mensual
                    valores.append(round(capital, 2))

                # Preparar los resultados
                resultado = {
                    'valor_final': round(valor_final, 2),
                    'valor_min': round(valor_min, 2),
                    'valor_max': round(valor_max, 2),
                    'monto_inicial': round(monto, 2),
                    'tipo_activo': tipo_activo.nombre,  # Aquí usamos el nombre de la inversión
                    'plazo_anos': round(t, 2),
                    'rentabilidad': round(rent * 100, 2),  # mostrar como %
                    'valores': valores
                }

                # Convertir a formato JSON
                resultado_json = json.dumps(resultado)

            except ConfiguracionActivo.DoesNotExist:
                resultado_json = json.dumps({"error": "Tipo de activo no encontrado"})

    return render(request, 'inversiones/inversiones.html', {
        'form': form,
        'resultado': resultado,
        'resultado_json': resultado_json
    })



def generar_pdf(request):
    if request.method == 'POST':
        resultado_json = request.POST.get('resultado_json')
        if not resultado_json:
            return HttpResponse("No se recibió resultado JSON", status=400)

        try:
            resultado_data = json.loads(resultado_json)
        except json.JSONDecodeError as e:
            return HttpResponse(f"Error de JSON: {e}", status=400)

        context = {
            'resultado': resultado_data
        }

     
        html = render_to_string('pdf/reporte_pdf.html', context=context, request=request)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="reporte_simulacion.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse('Error al generar PDF', status=500)

        return response