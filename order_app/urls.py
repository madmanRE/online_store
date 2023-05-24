from django.contrib import admin
from django.urls import include, path
from order_app.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = (
    [
        path("ordering/", OrderingPageView.as_view(), name="ordering"),
        path(
            "account/<int:profile_id>/order-history/",
            OrderHistoryView.as_view(),
            name="order_history",
        ),
        path("account/order/<int:hist_id>/", OneOrderView.as_view(), name="order_view"),
        path("cart/<int:product_id>/", add_to_cart, name="add-to-cart"),
        path("cart/", CartView.as_view(), name="cart"),
        path("payment/", FinishOrderHistory.as_view(), name="payment"),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
