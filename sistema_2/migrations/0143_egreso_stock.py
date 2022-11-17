# Generated by Django 4.1.2 on 2022-10-27 00:59

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0142_alter_facturas_observacionfactura'),
    ]

    operations = [
        migrations.CreateModel(
            name='egreso_stock',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('producto_id', models.CharField(max_length=32, null=True)),
                ('producto_codigo', models.CharField(max_length=32, null=True)),
                ('producto_nombre', models.CharField(default='', max_length=256)),
                ('almacen', models.CharField(max_length=32, null=True)),
                ('cantidad', models.CharField(max_length=32, null=True)),
                ('stock_anterior', models.CharField(default='0', max_length=32)),
                ('nuevo_stock', models.CharField(default='0', max_length=32)),
                ('fechaIngreso', models.CharField(max_length=32, null=True)),
                ('vendedorStock', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=128), null=True, size=None)),
                ('operacionIngreso', models.CharField(default='Egreso productos', max_length=64)),
                ('referencia', models.CharField(default='Egreso', max_length=64)),
            ],
        ),
    ]