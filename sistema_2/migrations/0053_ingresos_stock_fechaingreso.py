# Generated by Django 4.0.6 on 2022-07-17 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0052_boletas'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingresos_stock',
            name='fechaIngreso',
            field=models.CharField(max_length=32, null=True),
        ),
    ]
