# Generated by Django 4.2.2 on 2023-08-11 01:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0017_employer_sidebar_permissions'),
        ('financial', '0027_orderstatus_order'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderstatus',
            options={'ordering': ['created'], 'verbose_name': 'Order Status', 'verbose_name_plural': 'Order Status'},
        ),
        migrations.AlterUniqueTogether(
            name='paymentmethod',
            unique_together={('restaurant', 'title', 'method')},
        ),
    ]
