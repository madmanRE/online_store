# Generated by Django 4.0.6 on 2023-05-04 22:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("my_store_app", "0020_remove_orderhistory_product_order_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="orderhistory",
            name="order",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="my_store_app.order",
                verbose_name="заказ",
            ),
        ),
    ]
