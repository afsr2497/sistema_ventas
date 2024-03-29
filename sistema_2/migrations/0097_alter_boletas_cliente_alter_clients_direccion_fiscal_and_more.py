# Generated by Django 4.0.6 on 2022-08-11 17:02

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0096_boletas_nrodocumento_facturas_nrodocumento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boletas',
            name='cliente',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256), null=True, size=None),
        ),
        migrations.AlterField(
            model_name='clients',
            name='direccion_fiscal',
            field=models.CharField(default='SinDireccion', max_length=256),
        ),
        migrations.AlterField(
            model_name='cotizaciones',
            name='cliente',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256), null=True, size=None),
        ),
        migrations.AlterField(
            model_name='facturas',
            name='cliente',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256), null=True, size=None),
        ),
        migrations.AlterField(
            model_name='guias',
            name='cliente',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256), null=True, size=None),
        ),
        migrations.AlterField(
            model_name='notacredito',
            name='cliente',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=256), null=True, size=None),
        ),
    ]
