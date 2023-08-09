# Generated by Django 4.2.2 on 2023-08-09 02:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('financial', '0024_ordergroup_remove_order_bill_and_more'),
        ('delivery', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='deliveryorder',
            name='order_group',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_order', to='financial.ordergroup', verbose_name='Order group'),
        ),
        migrations.AddField(
            model_name='clientadress',
            name='client',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adresses', to='delivery.client', verbose_name='Client'),
        ),
    ]
