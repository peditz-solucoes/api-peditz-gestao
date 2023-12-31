# Generated by Django 4.2.2 on 2023-06-29 20:12

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('financial', '0006_order_order_number'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashier',
            name='opened_by',
            field=models.ForeignKey(on_delete=models.SET('Usuário deletado'), related_name='cashier_opened_by', to=settings.AUTH_USER_MODEL, verbose_name='Opened by'),
        ),
    ]
