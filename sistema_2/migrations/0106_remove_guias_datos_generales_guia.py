# Generated by Django 4.1 on 2022-08-22 03:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0105_guias_datos_generales_guia_guias_datos_raros_guia'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guias',
            name='datos_generales_guia',
        ),
    ]
