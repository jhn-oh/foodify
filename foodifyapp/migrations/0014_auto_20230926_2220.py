# Generated by Django 3.2.19 on 2023-09-26 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodifyapp', '0013_auto_20230923_2137'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='max_spicy',
            field=models.IntegerField(default=5),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='username',
            field=models.TextField(blank=True, default='default_username', null=True),
        ),
    ]