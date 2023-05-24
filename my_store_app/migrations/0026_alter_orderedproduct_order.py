# Generated by Django 4.0.6 on 2023-05-06 06:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("my_store_app", "0025_orderedproduct"),
    ]

    operations = [
        migrations.AlterField(
            model_name="orderedproduct",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="my_store_app.orderhistory",
            ),
        ),
    ]
