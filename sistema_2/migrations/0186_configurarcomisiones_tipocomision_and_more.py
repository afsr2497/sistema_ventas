# Generated by Django 4.1.7 on 2023-04-02 20:10

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0185_configurarcomisiones_fecharegistro'),
    ]

    operations = [
        migrations.AddField(
            model_name='configurarcomisiones',
            name='tipoComision',
            field=models.CharField(default='PARCIAL', max_length=32),
        ),
        migrations.AddField(
            model_name='configurarcomisiones',
            name='usuariosComision',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=32), size=None), default=[], size=None),
        ),
    ]
