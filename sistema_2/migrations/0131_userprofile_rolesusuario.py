# Generated by Django 4.1.1 on 2022-09-29 21:54

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0130_regoperacion_conectado_abono'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='rolesUsuario',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), default=['1', '1', '1'], size=None),
        ),
    ]
