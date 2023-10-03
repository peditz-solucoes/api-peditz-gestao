# Generated by Django 4.2.2 on 2023-09-02 22:42

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0039_remove_complementprice_catalog_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employer',
            name='code',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='employer',
            name='phone',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, default='', max_length=128, region='BR', verbose_name='Phone'),
        ),
    ]