# Generated by Django 4.1.1 on 2022-09-29 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0127_rename_banco_datos_abonosoperacion_datos_banco'),
    ]

    operations = [
        migrations.AddField(
            model_name='abonosoperacion',
            name='conectado',
            field=models.CharField(default='0', max_length=64),
        ),
    ]