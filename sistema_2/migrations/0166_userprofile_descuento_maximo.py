# Generated by Django 4.1.4 on 2023-01-02 00:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0165_rename_max_endedudamiento_clients_max_endeudamiento'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='descuento_maximo',
            field=models.CharField(default='0', max_length=24),
        ),
    ]