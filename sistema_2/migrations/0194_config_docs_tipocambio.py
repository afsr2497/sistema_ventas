# Generated by Django 4.2.1 on 2023-05-16 19:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0193_ingresoscaja_fechaingreso'),
    ]

    operations = [
        migrations.AddField(
            model_name='config_docs',
            name='tipoCambio',
            field=models.CharField(default='0', max_length=8),
        ),
    ]
