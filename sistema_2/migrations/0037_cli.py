# Generated by Django 4.0.4 on 2022-07-05 23:05

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0036_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='cli',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=64, null=True)),
                ('apellido', models.CharField(max_length=64, null=True)),
                ('razon_social', models.CharField(max_length=128, null=True)),
                ('dni', models.CharField(max_length=64, null=True)),
                ('ruc', models.CharField(max_length=64, null=True)),
                ('email', models.CharField(max_length=64, null=True)),
                ('contacto', models.CharField(max_length=64, null=True)),
                ('telefono', models.CharField(max_length=64, null=True)),
                ('direcciones', django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=20), size=None), null=True, size=None)),
            ],
        ),
    ]
