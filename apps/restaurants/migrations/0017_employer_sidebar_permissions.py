# Generated by Django 4.2.2 on 2023-08-08 02:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0016_sidebar'),
    ]

    operations = [
        migrations.AddField(
            model_name='employer',
            name='sidebar_permissions',
            field=models.ManyToManyField(blank=True, to='restaurants.sidebar'),
        ),
    ]
