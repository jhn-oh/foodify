# Generated by Django 4.2.2 on 2023-07-24 08:05

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restaurantName_ko', models.CharField(max_length=100)),
                ('restaurantName_en', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('menuName_ko', models.CharField(max_length=100)),
                ('menuName_en', models.CharField(max_length=100)),
                ('menuType', models.CharField(max_length=100)),
                ('menuTypeCode', models.IntegerField()),
                ('origin', models.CharField(choices=[('C', 'Chinese'), ('J', 'Japanese'), ('K', 'Korean'), ('W', 'Western')], max_length=1)),
                ('price', models.IntegerField()),
                ('rating', models.FloatField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Restaurant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('restaurantName_ko', models.CharField(max_length=100)),
                ('restaurantName_en', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=500)),
                ('direction_link', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_of_recommendations', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liked_food', models.CharField(max_length=1000)),
                ('disliked_food', models.CharField(max_length=1000)),
                ('log', models.JSONField()),
            ],
        ),
    ]
