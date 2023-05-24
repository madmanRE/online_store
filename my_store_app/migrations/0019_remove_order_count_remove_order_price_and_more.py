# Generated by Django 4.0.6 on 2023-05-03 18:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("my_store_app", "0018_remove_basket_product_basketitem"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="order",
            name="count",
        ),
        migrations.RemoveField(
            model_name="order",
            name="price",
        ),
        migrations.RemoveField(
            model_name="order",
            name="product_order",
        ),
        migrations.AddField(
            model_name="order",
            name="current_basket",
            field=models.ForeignKey(
                default=0,
                on_delete=django.db.models.deletion.CASCADE,
                to="my_store_app.basket",
                verbose_name="товары в корзине",
            ),
            preserve_default=False,
        ),
    ]
