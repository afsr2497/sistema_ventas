# Generated by Django 4.0.6 on 2022-07-18 20:18

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0059_boletas_fechavencboleta_facturas_fechavencfactura'),
    ]

    operations = [
        migrations.AddField(
            model_name='guias',
            name='datosTraslado',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64, null=True), null=True, size=None),
        ),
    ]
