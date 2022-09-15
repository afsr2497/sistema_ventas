# Generated by Django 4.1 on 2022-09-15 09:13

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sistema_2", "0122_facturas_codigoscotis_guias_cotirelacionada"),
    ]

    operations = [
        migrations.AddField(
            model_name="regoperacion",
            name="clienteExcel",
            field=models.CharField(default="", max_length=256),
        ),
        migrations.AlterField(
            model_name="facturas",
            name="codigosCotis",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=128), default=[], size=None
            ),
        ),
        migrations.AlterField(
            model_name="facturas",
            name="codigosGuias",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=128), default=[], size=None
            ),
        ),
    ]