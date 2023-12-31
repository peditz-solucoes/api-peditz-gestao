# Generated by Django 4.2.2 on 2023-11-09 19:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0035_takeoutorder_sequence'),
        ('delivery', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryorder',
            name='payment_method',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments_methods', to='financial.paymentmethod', verbose_name='Payment Method'),
        ),
        migrations.AddField(
            model_name='deliveryorder',
            name='payment_method_title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Payment Method title'),
        ),
    ]
