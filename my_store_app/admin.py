from django.contrib import admin
from my_store_app.models import *


class ProductImageInline(admin.TabularInline):
    model = Product.gallery.through


class SalesAdmin(admin.ModelAdmin):
    list_display = ["product", "shop", "count", "dateFrom", "dateTo"]
    search_fields = ["product"]


class CategoryProductAdmin(admin.ModelAdmin):
    list_display = ["title", "image"]
    search_fields = ["title"]


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "category",
        "price",
        "count",
        "short_description",
        "rating",
    ]

    search_fields = ["title"]
    list_display_links = [
        "title",
    ]

    inlines = [ProductImageInline]

    exclude = ["gallery"]

    def short_description(self, obj):
        if len(obj.description) > 50:
            return obj.description[:50] + "..."
        else:
            return obj.description

    short_description.short_description = "Описание"


class TagsFileAdmin(admin.ModelAdmin):
    list_display = ["tags_name"]
    search_fields = ["tags_name"]


class ReviewsAdmin(admin.ModelAdmin):
    list_display = ["text", "product", "author", "create_at"]
    search_fields = ["author"]


class SpecificationsAdmin(admin.ModelAdmin):
    list_display = ["name", "value"]
    search_fields = ["name"]


class ShopAdmin(admin.ModelAdmin):
    list_display = ["shop_name"]
    search_fields = ["shop_name"]


class LimitedOfferAdmin(admin.ModelAdmin):
    list_display = ["product", "new_price", "duration"]


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ["product_ref", "image"]


admin.site.register(CategoryProduct, CategoryProductAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Reviews, ReviewsAdmin)
admin.site.register(TagsFile, TagsFileAdmin)
admin.site.register(Specifications, SpecificationsAdmin)
admin.site.register(Shop, ShopAdmin)
admin.site.register(Sales, SalesAdmin)
admin.site.register(LimitedOffer, LimitedOfferAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
