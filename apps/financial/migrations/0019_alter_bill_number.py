# Generated by Django 4.2.2 on 2023-08-08 01:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0018_alter_bill_opened_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='number',
            field=models.PositiveBigIntegerField(verbose_name='Number'),
        ),
    ]