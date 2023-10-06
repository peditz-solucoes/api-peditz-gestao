# Generated by Django 4.2.2 on 2023-10-06 11:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0003_remove_item_relatedproducts_productitem_itemitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='itemtransaction',
            name='notes',
            field=models.TextField(blank=True, default='', null=True, verbose_name='Notes'),
        ),
        migrations.AlterField(
            model_name='itemtransaction',
            name='total',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Total'),
        ),
        migrations.AlterField(
            model_name='itemtransaction',
            name='unit_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Unit Price'),
        ),
    ]
