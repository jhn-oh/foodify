# Generated by Django 3.2.6 on 2023-08-21 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodifyapp', '0006_auto_20230821_1629'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='rating',
            field=models.FloatField(default=0, null=True),
        ),
    ]