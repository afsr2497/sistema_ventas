# Generated by Django 4.1.2 on 2022-10-26 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0140_facturas_observacionfactura'),
    ]

    operations = [
        migrations.AlterField(
            model_name='facturas',
            name='observacionFactura',
            field=models.CharField(max_length=512, null=True),
        ),
    ]