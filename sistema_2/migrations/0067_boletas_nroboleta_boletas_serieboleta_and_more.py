# Generated by Django 4.0.6 on 2022-07-21 18:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0066_rename_boletaseria_config_docs_boletaserie'),
    ]

    operations = [
        migrations.AddField(
            model_name='boletas',
            name='nroBoleta',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='boletas',
            name='serieBoleta',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='facturas',
            name='nroFactura',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='facturas',
            name='serieFactura',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='guias',
            name='nroGuia',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='guias',
            name='serieGuia',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
