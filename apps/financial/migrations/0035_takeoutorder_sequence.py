# Generated by Django 4.2.2 on 2023-10-13 04:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('financial', '0034_ordergroup_notes_alter_takeoutorder_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='takeoutorder',
            name='sequence',
            field=models.PositiveIntegerField(default=0, verbose_name='Sequence'),
        ),
    ]
