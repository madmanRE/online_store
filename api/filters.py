from django_filters import rest_framework as filters
from my_store_app.models import Product
from blog_app.models import Article


class ProductFilter(filters.FilterSet):
    title = filters.CharFilter(field_name='title', lookup_expr='icontains')

    class Meta:
        model = Product
        fields = {
            'price': ['lte', 'exact', 'gte']
        }


class ArticleFilter(filters.FilterSet):
    theme_title = filters.CharFilter(field_name='theme__title', lookup_expr='icontains')

    class Meta:
        model = Article
        fields = {
        }
