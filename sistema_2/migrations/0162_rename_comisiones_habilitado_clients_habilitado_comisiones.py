# Generated by Django 4.1.4 on 2023-01-01 04:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0161_clients_comisiones_habilitado'),
    ]

    operations = [
        migrations.RenameField(
            model_name='clients',
            old_name='comisiones_habilitado',
            new_name='habilitado_comisiones',
        ),
    ]