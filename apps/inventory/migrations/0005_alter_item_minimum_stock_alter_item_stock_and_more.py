# Generated by Django 4.2.2 on 2023-10-06 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_itemtransaction_notes_alter_itemtransaction_total_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='minimum_stock',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=20, verbose_name='Minimum stock'),
        ),
        migrations.AlterField(
            model_name='item',
            name='stock',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=20, verbose_name='stock'),
        ),
        migrations.AlterField(
            model_name='itemtransaction',
            name='quantity',
            field=models.DecimalField(decimal_places=3, max_digits=20, verbose_name='Quantity'),
        ),
        migrations.AlterField(
            model_name='itemtransaction',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Total'),
        ),
        migrations.AlterField(
            model_name='itemtransaction',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=20, verbose_name='Unit Price'),
        ),
    ]
