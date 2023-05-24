from rest_framework.response import Response
from rest_framework.decorators import api_view
from blog_app.models import Article, Theme
from .serializers import ArticleSerializer, ArticleDetailSerializer, ProductDetailSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from my_store_app.models import Product, CategoryProduct
from .filters import ProductFilter, ArticleFilter
from rest_framework import filters
from django_filters import rest_framework as django_filters
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin


class ArticleDetailView(RetrieveAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleDetailSerializer


class ProductListApiView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ProductDetailSerializer
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


class ArticleListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ArticleDetailSerializer
    queryset = Article.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = ArticleFilter
