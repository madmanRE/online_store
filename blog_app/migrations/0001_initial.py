# Generated by Django 4.0.6 on 2023-05-21 17:02

import blog_app.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('my_store_app', '0033_orderhistory_confirmed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30)),
                ('slug', models.SlugField(max_length=90, unique=True)),
            ],
            options={
                'verbose_name': 'Тема',
                'verbose_name_plural': 'Темы',
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('text', models.TextField(max_length=50000)),
                ('date', models.DateField(auto_now_add=True)),
                ('slug', models.SlugField(blank=True, max_length=90, unique=True)),
                ('image', models.ImageField(blank=True, default=None, null=True, upload_to=blog_app.models.create_image_path_for_article)),
                ('rating', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('author', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='my_store_app.profile')),
                ('theme', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='articles', to='blog_app.theme')),
            ],
            options={
                'verbose_name': 'статья',
                'verbose_name_plural': 'статьи',
            },
        ),
    ]