# Generated by Django 4.1 on 2022-08-22 03:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0107_guias_nuevos_datos_migrados'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guias',
            name='nuevos_datos_migrados',
        ),
    ]
