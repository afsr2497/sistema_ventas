# Generated by Django 4.2.2 on 2023-07-07 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0195_ordencomprametalprotec_mostrarvu'),
    ]

    operations = [
        migrations.AddField(
            model_name='guias',
            name='licenciaConductor',
            field=models.CharField(default='', max_length=24),
        ),
    ]
