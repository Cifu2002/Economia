from django.contrib import admin
from .models import ConfiguracionActivo

class ConfiguracionActivoAdmin(admin.ModelAdmin):
    # Eliminando 'capitalizacion' de 'list_display' y 'list_filter'
    list_display = ('tipo', 'rentabilidad_esperada', 'volatilidad', 'comision')  # Sin 'capitalizacion'
    list_filter = ('tipo',)  # Sin 'capitalizacion'

admin.site.register(ConfiguracionActivo, ConfiguracionActivoAdmin)
