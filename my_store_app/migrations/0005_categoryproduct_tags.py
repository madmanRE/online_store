# Generated by Django 4.0.6 on 2023-04-23 15:23

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("my_store_app", "0004_product_limited_edition"),
    ]

    operations = [
        migrations.AddField(
            model_name="categoryproduct",
            name="tags",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="my_store_app.tagsfile",
                verbose_name="теги категории",
            ),
        ),
    ]
