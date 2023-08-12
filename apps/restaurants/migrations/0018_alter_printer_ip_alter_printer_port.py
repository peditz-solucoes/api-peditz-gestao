# Generated by Django 4.2.2 on 2023-08-12 17:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('restaurants', '0017_employer_sidebar_permissions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='printer',
            name='ip',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='printer',
            name='port',
            field=models.IntegerField(blank=True, default=9100, null=True),
        ),
    ]
