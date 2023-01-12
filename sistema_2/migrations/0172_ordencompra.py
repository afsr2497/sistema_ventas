# Generated by Django 4.1.5 on 2023-01-11 17:20

import datetime
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0171_products_producto_a_products_producto_b_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ordenCompra',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fechaOrden', models.DateField(default=datetime.date.today)),
                ('proveedorCodigo', models.CharField(default='000000', max_length=64)),
                ('proveedorNombre', models.CharField(default='', max_length=64)),
                ('usuarioOrden', models.CharField(default='', max_length=64)),
                ('monedaOrden', models.CharField(default='SOLED', max_length=64)),
                ('productos', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), size=None), default=[], size=None)),
                ('direccion', models.CharField(default='', max_length=64)),
                ('destino', models.CharField(default='', max_length=64)),
                ('ruc_proveedor', models.CharField(default='', max_length=64)),
                ('codigo_orden', models.CharField(default='', max_length=64)),
                ('estado_orden', models.CharField(default='', max_length=64)),
            ],
        ),
    ]