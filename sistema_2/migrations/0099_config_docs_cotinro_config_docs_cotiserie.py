# Generated by Django 4.0.6 on 2022-08-12 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0098_cotizaciones_imprimirpu_cotizaciones_imprimirvu_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='config_docs',
            name='cotiNro',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='config_docs',
            name='cotiSerie',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
