# Generated by Django 4.1.2 on 2022-10-24 02:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0136_alter_userprofile_rolesusuario'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingresos_stock',
            name='operacionIngreso',
            field=models.CharField(default='Ingreso productos', max_length=64),
        ),
    ]
