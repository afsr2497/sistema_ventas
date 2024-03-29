# Generated by Django 4.1.5 on 2023-02-23 05:19

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0178_kitsproductos'),
    ]

    operations = [
        migrations.AddField(
            model_name='products',
            name='producto_C',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), default=[], size=None),
        ),
        migrations.AddField(
            model_name='products',
            name='producto_D',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), default=[], size=None),
        ),
        migrations.AddField(
            model_name='products',
            name='producto_E',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=64), default=[], size=None),
        ),
    ]
