# Generated by Django 4.1.5 on 2023-01-22 22:54

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0174_abonosoperacion_abono_comisionable'),
    ]

    operations = [
        migrations.AddField(
            model_name='boletas',
            name='codigosCotis',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=128), default=[], size=None),
        ),
    ]