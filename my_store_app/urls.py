from django.contrib import admin
from django.urls import include, path
from my_store_app.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = (
    [
        path("", CategoryView.as_view(), name="index"),
        path("catalog/filter/", product_filter, name="product_filter"),
        path("catalog/", CatalogView.as_view(), name="catalog"),
        path(
            "catalog/<slug:category_slug>/",
            CategoryDetailView.as_view(),
            name="category",
        ),
        path("catalog/tags/<int:tag_id>/", TagPageView.as_view(), name="tag_page"),
        path(
            "catalog/product/<slug:product_slug>/",
            ProductDetailView.as_view(),
            name="product",
        ),
        path("search/", search, name="search"),
        path("about/", AboutUsView.as_view(), name="about"),
        path("api/", api_view, name="api"),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
