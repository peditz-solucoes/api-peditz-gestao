# Generated by Django 4.2.2 on 2023-10-06 15:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_alter_itemtransaction_user'),
    ]

    operations = [
        migrations.RenameField(
            model_name='itemitem',
            old_name='item_related',
            new_name='ingredient',
        ),
    ]
