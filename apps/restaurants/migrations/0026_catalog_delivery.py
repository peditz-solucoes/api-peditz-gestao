# Generated by Django 4.2.2 on 2023-08-20 13:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0025_productprice_tag'),
    ]

    operations = [
        migrations.AddField(
            model_name='catalog',
            name='delivery',
            field=models.BooleanField(default=False),
        ),
    ]