# Generated by Django 4.2.2 on 2023-08-20 14:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0028_productcomplementprice_product_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcomplementprice',
            name='product_complement_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complement_prices', to='restaurants.productcomplementitem'),
        ),
    ]
