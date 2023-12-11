# Generated by Django 4.2.2 on 2023-12-03 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0039_order_active_cancelationreason'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmethod',
            name='acept_on_delivery',
            field=models.BooleanField(default=True, verbose_name='Acept on delivery'),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='needs_change',
            field=models.BooleanField(default=False, verbose_name='Needs change'),
        ),
    ]