# Generated by Django 4.1.7 on 2023-04-26 19:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0191_registrocosto_cajarelacionada'),
    ]

    operations = [
        migrations.AddField(
            model_name='cajachica',
            name='fechaCreacion',
            field=models.DateField(default=datetime.datetime.today),
        ),
        migrations.AddField(
            model_name='cajachica',
            name='monedaCaja',
            field=models.CharField(default='SOLES', max_length=16),
        ),
    ]
