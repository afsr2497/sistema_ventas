# Generated by Django 4.1.3 on 2022-12-17 20:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0156_guias_origenguia'),
    ]

    operations = [
        migrations.AddField(
            model_name='cotizaciones',
            name='mostrarCabos',
            field=models.CharField(default='0', max_length=64),
        ),
        migrations.AddField(
            model_name='cotizaciones',
            name='mostrarPanhos',
            field=models.CharField(default='0', max_length=64),
        ),
    ]
