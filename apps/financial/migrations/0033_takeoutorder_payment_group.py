# Generated by Django 4.2.2 on 2023-10-06 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0032_alter_paymentmethod_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='takeoutorder',
            name='payment_group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='takeout_orders', to='financial.paymentgroup', verbose_name='Payment Group'),
        ),
    ]
