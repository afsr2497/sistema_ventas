# Generated by Django 4.1.1 on 2022-09-29 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0128_abonosoperacion_conectado'),
    ]

    operations = [
        migrations.AddField(
            model_name='abonosoperacion',
            name='idRegistroOp',
            field=models.CharField(default='0', max_length=64),
        ),
    ]