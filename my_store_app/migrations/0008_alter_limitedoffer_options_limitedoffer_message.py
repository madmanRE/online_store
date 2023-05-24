# Generated by Django 4.0.6 on 2023-04-23 18:36

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("my_store_app", "0007_alter_product_price_limitedoffer"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="limitedoffer",
            options={
                "verbose_name": "Специальное предложение",
                "verbose_name_plural": "Специальные предложения",
            },
        ),
        migrations.AddField(
            model_name="limitedoffer",
            name="message",
            field=models.CharField(
                blank=True, max_length=500, null=True, verbose_name="описание"
            ),
        ),
    ]
