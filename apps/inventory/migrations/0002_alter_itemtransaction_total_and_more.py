# Generated by Django 4.2.2 on 2023-06-29 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemtransaction',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='Total'),
        ),
        migrations.AlterField(
            model_name='itemtransaction',
            name='user_name',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='User name'),
        ),
    ]
