from django.db import models

class SiteConfiguration(models.Model):
    site_terms = models.TextField(max_length=500,default="Terminos y Condiciones")
    site_name = models.CharField(max_length=255, default="Mi Sitio")
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)

    def __str__(self):
        return "Configuración del sitio"

    class Meta:
        verbose_name = "Configuración del sitio"
        verbose_name_plural = "Configuración del sitio"
        
