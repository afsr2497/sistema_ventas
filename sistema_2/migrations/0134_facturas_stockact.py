# Generated by Django 4.1.2 on 2022-10-12 12:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0133_abonosoperacion_comprobantecancelado'),
    ]

    operations = [
        migrations.AddField(
            model_name='facturas',
            name='stockAct',
            field=models.CharField(default='0', max_length=64),
        ),
    ]
