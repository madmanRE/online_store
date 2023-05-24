from django.contrib import admin
from my_store_app.models import *


class BasketAdmin(admin.ModelAdmin):
    list_display = ["username", "create_at"]
    search_fields = ["username"]


class PaymentAdmin(admin.ModelAdmin):
    list_display = ["number", "name", "month", "year", "code"]
    search_fields = ["number"]


class OrderAdmin(admin.ModelAdmin):
    list_display = ["current_basket", "date", "free_delivery", "pk"]


class OrderHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "user_order",
        "get_product_order",
        "payment_date",
        "delivery_type",
        "payment_type",
        "total_cost",
        "status",
        "city",
        "address",
        "confirmed",
    )

    def get_product_order(self, obj):
        return ", ".join(
            str(x) for x in obj.product_order.values_list("title", flat=True)
        )

    get_product_order.short_description = "Product Order"


class OrderedProductAdmin(admin.ModelAdmin):
    list_display = ["product", "order", "quantity"]


admin.site.register(Basket, BasketAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderHistory, OrderHistoryAdmin)
admin.site.register(OrderedProduct, OrderedProductAdmin)
