# Generated by Django 4.0.6 on 2023-04-23 18:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("my_store_app", "0006_remove_categoryproduct_tags_categoryproduct_tags"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(
                decimal_places=2, max_digits=10, verbose_name="цена товара"
            ),
        ),
        migrations.CreateModel(
            name="LimitedOffer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "new_price",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="новая цена"
                    ),
                ),
                ("duration", models.DurationField(verbose_name="время до конца акции")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="my_store_app.product",
                        verbose_name="товар",
                    ),
                ),
            ],
        ),
    ]