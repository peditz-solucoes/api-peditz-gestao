# Generated by Django 4.2.2 on 2023-08-09 02:29

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import localflavor.br.models
import model_utils.fields
import phonenumber_field.modelfields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('restaurants', '0017_employer_sidebar_permissions'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128, region='BR', verbose_name='Phone')),
                ('cpf', localflavor.br.models.BRCPFField(blank=True, max_length=14, null=True, verbose_name='CPF')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email')),
                ('verified_email', models.BooleanField(default=False, verbose_name='Verified email')),
                ('verified_phone', models.BooleanField(default=False, verbose_name='Verified phone')),
            ],
            options={
                'verbose_name': 'Client',
                'verbose_name_plural': 'Clients',
            },
        ),
        migrations.CreateModel(
            name='ClientAdress',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('street', models.CharField(max_length=255, verbose_name='Street')),
                ('number', models.CharField(max_length=255, verbose_name='Number')),
                ('complement', models.CharField(blank=True, max_length=255, null=True, verbose_name='Complement')),
                ('neighborhood', models.CharField(max_length=255, verbose_name='Neighborhood')),
                ('city', models.CharField(max_length=255, verbose_name='City')),
                ('state', localflavor.br.models.BRStateField(max_length=2, verbose_name='State')),
                ('postal_code', localflavor.br.models.BRPostalCodeField(max_length=9, verbose_name='Postal code')),
                ('main', models.BooleanField(default=False, verbose_name='Main')),
                ('title', models.CharField(blank=True, default='Casa', max_length=255, null=True, verbose_name='Title')),
            ],
            options={
                'verbose_name': 'Client adress',
                'verbose_name_plural': 'Client adresses',
            },
        ),
        migrations.CreateModel(
            name='DeliveryRestaurantConfig',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('delivery_base_time', models.IntegerField(default=0, verbose_name='Delivery base time')),
                ('enable_delivery', models.BooleanField(default=False, verbose_name='Enable delivery')),
                ('price_per_km', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Price per km')),
                ('base_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Base price')),
                ('free_delivery_min_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Free delivery min price')),
                ('free_delivery_max_distance', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Free delivery max distance')),
                ('restaurant', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_config', to='restaurants.restaurant', verbose_name='Restaurant')),
            ],
            options={
                'verbose_name': 'Delivery restaurant config',
                'verbose_name_plural': 'Delivery restaurant configs',
            },
        ),
        migrations.CreateModel(
            name='DeliveryOrder',
            fields=[
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('id', model_utils.fields.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('client_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Client name')),
                ('client_phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region='BR', verbose_name='Client phone')),
                ('street', models.CharField(blank=True, max_length=255, null=True, verbose_name='Street')),
                ('number', models.CharField(blank=True, max_length=255, null=True, verbose_name='Number')),
                ('complement', models.CharField(blank=True, max_length=255, null=True, verbose_name='Complement')),
                ('neighborhood', models.CharField(blank=True, max_length=255, null=True, verbose_name='Neighborhood')),
                ('city', models.CharField(blank=True, max_length=255, null=True, verbose_name='City')),
                ('state', localflavor.br.models.BRStateField(blank=True, max_length=2, null=True, verbose_name='State')),
                ('postal_code', localflavor.br.models.BRPostalCodeField(blank=True, max_length=9, null=True, verbose_name='Postal code')),
                ('type', models.CharField(choices=[('IFOOD', 'Ifood'), ('DELIVERY_APP', 'Delivery App'), ('DELIVERY_SITE', 'Delivery Site')], default='DELIVERY_SITE', max_length=255, verbose_name='Type')),
                ('delivery_price', models.DecimalField(decimal_places=2, default=0.0, max_digits=10, verbose_name='Delivery price')),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='delivery_orders', to='delivery.client', verbose_name='Client')),
            ],
            options={
                'verbose_name': 'Delivery order',
                'verbose_name_plural': 'Delivery orders',
            },
        ),
    ]
