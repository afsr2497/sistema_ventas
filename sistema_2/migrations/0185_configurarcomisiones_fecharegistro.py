# Generated by Django 4.1.7 on 2023-03-30 17:46

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0184_rename_configcomisiones_configurarcomisiones'),
    ]

    operations = [
        migrations.AddField(
            model_name='configurarcomisiones',
            name='fechaRegistro',
            field=models.DateField(default=datetime.datetime.today),
        ),
    ]