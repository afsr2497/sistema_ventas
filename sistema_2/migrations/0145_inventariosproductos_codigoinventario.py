# Generated by Django 4.1.2 on 2022-10-31 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0144_inventariosproductos'),
    ]

    operations = [
        migrations.AddField(
            model_name='inventariosproductos',
            name='codigoInventario',
            field=models.CharField(default='INV-0000', max_length=32),
        ),
    ]
