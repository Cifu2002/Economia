# Generated by Django 5.2 on 2025-04-29 00:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nucleo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteconfiguration',
            name='site_terms',
            field=models.TextField(default='Terminos y Condiciones', max_length=500),
        ),
    ]
