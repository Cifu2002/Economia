# nucleo/context_processors.py

from .models import SiteConfiguration

def site_settings(request):
    config = SiteConfiguration.objects.first()
    logo_url = config.logo.url if config and config.logo else None
    full_logo_url = request.build_absolute_uri(logo_url) if logo_url else None
    return {
        'site_name': config.site_name if config else 'Mi Sitio',
        'site_logo': full_logo_url,
        'site_terms': config.site_terms if config else 'Términos y condiciones',
    }
