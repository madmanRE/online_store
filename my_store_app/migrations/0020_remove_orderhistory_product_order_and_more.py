# Generated by Django 4.0.6 on 2023-05-04 20:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("my_store_app", "0019_remove_order_count_remove_order_price_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="orderhistory",
            name="product_order",
        ),
        migrations.AddField(
            model_name="orderhistory",
            name="product_order",
            field=models.ManyToManyField(
                to="my_store_app.product", verbose_name="товары"
            ),
        ),
    ]
