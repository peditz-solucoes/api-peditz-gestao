# Generated by Django 4.2.2 on 2024-06-06 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0044_cancelationreason_bill_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentgroup',
            name='discount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Discount'),
        ),
    ]
