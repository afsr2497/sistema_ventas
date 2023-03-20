# Generated by Django 4.1.7 on 2023-03-19 22:47

import datetime
import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0179_products_producto_c_products_producto_d_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ordenCompraMetalprotec',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rucProveedor', models.CharField(default='', max_length=32)),
                ('fechaEmision', models.DateField(default=datetime.date.today)),
                ('condicionOrden', models.CharField(default='', max_length=32)),
                ('codigoOrden', models.CharField(default='', max_length=32)),
                ('direccionProveedor', models.CharField(default='', max_length=128)),
                ('nombreProveedor', models.CharField(default='', max_length=64)),
                ('ciudadCliente', models.CharField(default='', max_length=32)),
                ('destinoCliente', models.CharField(default='', max_length=128)),
                ('atencionCliente', models.CharField(default='', max_length=64)),
                ('monedaOrden', models.CharField(default='SOLES', max_length=24)),
                ('productosOrden', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), size=None), default=[], size=None)),
            ],
        ),
    ]
