# Generated by Django 4.2.2 on 2023-08-08 01:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('financial', '0017_remove_ordercomplement_note'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bill',
            name='opened_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bill_opened_by', to=settings.AUTH_USER_MODEL, verbose_name='Opened by'),
        ),
    ]
