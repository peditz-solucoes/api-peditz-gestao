# Generated by Django 4.2.2 on 2023-06-29 22:11

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('restaurants', '0010_alter_restaurant_owner'),
        ('financial', '0012_alter_order_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentmethod',
            name='method',
            field=models.CharField(choices=[('01', 'Dinheiro'), ('01', 'PIX'), ('03', 'Cartão de Crédito'), ('04', 'Cartão de Débito'), ('10', 'Vale Alimentação'), ('11', 'Vale Refeição'), ('99', 'Outros')], default='01', max_length=255, verbose_name='Method'),
        ),
        migrations.AddField(
            model_name='paymentmethod',
            name='restaurant',
            field=models.ForeignKey(default='33b2de37-4f69-4101-967b-1930780c8a76', on_delete=django.db.models.deletion.CASCADE, related_name='payment_methods', to='restaurants.restaurant', verbose_name='Restaurant'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='bill',
            name='opened_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='bill_opened_by', to=settings.AUTH_USER_MODEL, verbose_name='Opened by'),
        ),
        migrations.AlterField(
            model_name='cashier',
            name='closed_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cashier_closed_by', to=settings.AUTH_USER_MODEL, verbose_name='Closed by'),
        ),
        migrations.AlterField(
            model_name='cashier',
            name='opened_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='cashier_opened_by', to=settings.AUTH_USER_MODEL, verbose_name='Opened by'),
        ),
        migrations.AlterField(
            model_name='paymentmethod',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Title'),
        ),
        migrations.AlterUniqueTogether(
            name='paymentmethod',
            unique_together={('restaurant', 'title')},
        ),
    ]
