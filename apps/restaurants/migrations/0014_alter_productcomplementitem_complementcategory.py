# Generated by Django 4.2.2 on 2023-07-28 02:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0013_alter_productcomplementitem_complementcategory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productcomplementitem',
            name='complementCategory',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='complement_items', to='restaurants.productcomplementcategory'),
        ),
    ]