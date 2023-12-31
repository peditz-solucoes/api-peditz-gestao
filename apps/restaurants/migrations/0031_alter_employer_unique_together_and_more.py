# Generated by Django 4.2.2 on 2023-08-21 20:27

from django.db import migrations, models
import localflavor.br.models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0030_alter_productcomplementprice_product_complement_item'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='employer',
            unique_together={('code', 'restaurant')},
        ),
        migrations.AlterField(
            model_name='employer',
            name='address',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='employer',
            name='cpf',
            field=localflavor.br.models.BRCPFField(blank=True, max_length=14, null=True, verbose_name='CPF'),
        ),
        migrations.AlterField(
            model_name='employer',
            name='office',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='employer',
            name='sallary',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
