# Generated by Django 4.1.5 on 2023-02-19 00:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0177_notacredito_estadosunat_notacredito_stockact'),
    ]

    operations = [
        migrations.CreateModel(
            name='kitsProductos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('productos', models.ManyToManyField(to='sistema_2.products')),
            ],
        ),
    ]