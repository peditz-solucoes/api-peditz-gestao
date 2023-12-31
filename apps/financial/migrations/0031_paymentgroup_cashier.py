# Generated by Django 4.2.2 on 2023-08-11 03:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0030_takeoutorder_cashier'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentgroup',
            name='cashier',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='payment_groups', to='financial.cashier', verbose_name='Cashier'),
            preserve_default=False,
        ),
    ]
