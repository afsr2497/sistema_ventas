# Generated by Django 4.1.2 on 2022-10-24 02:40

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0137_ingresos_stock_operacioningreso'),
    ]

    operations = [
        migrations.AlterField(
            model_name='boletas',
            name='productos',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), size=None), default=[], size=None),
        ),
        migrations.AlterField(
            model_name='boletas',
            name='servicios',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), size=None), default=[], size=None),
        ),
        migrations.AlterField(
            model_name='cotizaciones',
            name='productos',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), size=None), default=[], size=None),
        ),
        migrations.AlterField(
            model_name='cotizaciones',
            name='servicios',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), size=None), default=[], size=None),
        ),
        migrations.AlterField(
            model_name='facturas',
            name='productos',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), size=None), default=[], size=None),
        ),
        migrations.AlterField(
            model_name='facturas',
            name='servicios',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), size=None), default=[], size=None),
        ),
        migrations.AlterField(
            model_name='guias',
            name='productos',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), size=None), default=[], size=None),
        ),
        migrations.AlterField(
            model_name='guias',
            name='servicios',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), size=None), default=[], size=None),
        ),
    ]
