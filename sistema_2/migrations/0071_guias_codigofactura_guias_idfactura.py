# Generated by Django 4.0.6 on 2022-07-31 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0070_ingresos_stock_vendedorstock'),
    ]

    operations = [
        migrations.AddField(
            model_name='guias',
            name='codigoFactura',
            field=models.CharField(max_length=64, null=True),
        ),
        migrations.AddField(
            model_name='guias',
            name='idFactura',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
