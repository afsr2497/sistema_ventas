# Generated by Django 4.1.3 on 2022-11-19 02:29

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0149_notacredito_modonota'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notacredito',
            name='fechaEmision',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
