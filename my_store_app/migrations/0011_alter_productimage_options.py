# Generated by Django 4.0.6 on 2023-04-23 19:58

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("my_store_app", "0010_productimage_product_gallery"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="productimage",
            options={
                "verbose_name": "галерея изображений",
                "verbose_name_plural": "галереи изображений",
            },
        ),
    ]