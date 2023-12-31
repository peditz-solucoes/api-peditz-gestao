# Generated by Django 4.2.2 on 2023-06-29 22:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0010_alter_bill_opened_by_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_method',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='payments', to='financial.paymentmethod', verbose_name='Payment Method'),
        ),
    ]
