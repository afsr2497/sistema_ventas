# Generated by Django 4.0.6 on 2022-08-03 05:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0075_notacredito'),
    ]

    operations = [
        migrations.AddField(
            model_name='notacredito',
            name='codigoComprobante',
            field=models.CharField(max_length=64, null=True),
        ),
    ]
