# Generated by Django 4.0.6 on 2023-05-21 17:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='theme',
            name='slug',
            field=models.SlugField(blank=True, max_length=90, unique=True),
        ),
    ]
