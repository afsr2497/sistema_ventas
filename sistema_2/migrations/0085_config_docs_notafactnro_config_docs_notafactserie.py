# Generated by Django 4.0.6 on 2022-08-03 23:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sistema_2', '0084_notacredito_nronota_notacredito_serienota'),
    ]

    operations = [
        migrations.AddField(
            model_name='config_docs',
            name='notaFactNro',
            field=models.CharField(max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='config_docs',
            name='notaFactSerie',
            field=models.CharField(max_length=128, null=True),
        ),
    ]
