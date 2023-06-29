# Generated by Django 4.2.2 on 2023-06-29 17:00

import apps.restaurants.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0005_product_codigo_ncm_product_codigo_produto_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Catalog',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('slug', models.SlugField(max_length=255)),
                ('order', models.IntegerField(default=0)),
                ('active', models.BooleanField(default=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to=apps.restaurants.models.upload_path_catalogs)),
                ('products', models.ManyToManyField(blank=True, related_name='catalogs', to='restaurants.product')),
                ('restaurant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='catalogs', to='restaurants.restaurant')),
            ],
            options={
                'verbose_name': 'Catalog',
                'verbose_name_plural': 'Catalogs',
                'unique_together': {('restaurant', 'slug')},
            },
        ),
    ]
