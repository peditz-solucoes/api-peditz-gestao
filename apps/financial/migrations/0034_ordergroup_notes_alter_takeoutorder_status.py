# Generated by Django 4.2.2 on 2023-10-06 17:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0033_takeoutorder_payment_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordergroup',
            name='notes',
            field=models.TextField(blank=True, null=True, verbose_name='Notes'),
        ),
        migrations.AlterField(
            model_name='takeoutorder',
            name='status',
            field=models.CharField(choices=[('PAID', 'PAID'), ('CANCELED', 'CANCELED')], default='PAID', max_length=255, verbose_name='Status'),
        ),
    ]