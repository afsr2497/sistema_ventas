# Generated by Django 4.1 on 2022-09-11 20:54

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sistema_2", "0121_alter_clients_direccion_fiscal"),
    ]

    operations = [
        migrations.AddField(
            model_name="facturas",
            name="codigosCotis",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=128), null=True, size=None
            ),
        ),
        migrations.AddField(
            model_name="guias",
            name="cotiRelacionada",
            field=models.CharField(default="", max_length=128),
        ),
    ]
