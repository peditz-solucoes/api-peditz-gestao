# Generated by Django 4.2.2 on 2023-06-29 01:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0003_table'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='employer',
            unique_together={('cpf', 'restaurant'), ('phone', 'restaurant'), ('code', 'restaurant')},
        ),
    ]
