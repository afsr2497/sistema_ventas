# Generated by Django 4.1 on 2022-09-01 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sistema_2", "0119_boletas_registroboleta_facturas_registrofactura"),
    ]

    operations = [
        migrations.AddField(
            model_name="cotizaciones",
            name="registroCoti",
            field=models.CharField(default="0", max_length=64),
        ),
    ]