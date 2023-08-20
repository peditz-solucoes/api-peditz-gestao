# Generated by Django 4.2.2 on 2023-08-20 13:49

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0023_restaurant_active_restaurant_close_time_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='catalog',
            name='products',
        ),
        migrations.CreateModel(
            name='ProductPrice',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='prices', to='restaurants.product')),
            ],
            options={
                'verbose_name': 'Product Price',
                'verbose_name_plural': 'Product Prices',
                'ordering': ['product__title'],
            },
        ),
        migrations.AddField(
            model_name='catalog',
            name='products_prices',
            field=models.ManyToManyField(blank=True, related_name='catalogs', to='restaurants.productprice'),
        ),
    ]