from rest_framework import serializers
from blog_app.models import Article, Theme
from my_store_app.models import Profile, Product, CategoryProduct


class ArticleSerializer(serializers.ModelSerializer):
    short_text = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ('id', 'title', 'short_text', 'date', 'author_name', 'theme')

    def get_short_text(self, obj):
        return obj.text[:50]

    def get_author_name(self, obj):
        return obj.author.username


class ArticleDetailSerializer(serializers.ModelSerializer):
    short_text = serializers.SerializerMethodField()
    author_name = serializers.SerializerMethodField()
    theme_title = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ('id', 'title', 'short_text', 'date', 'author_name', 'slug', 'theme_title')

    def get_short_text(self, obj):
        return obj.text[:50]

    def get_author_name(self, obj):
        return obj.author.username

    def get_theme_title(self, obj):
        return obj.theme.title


class ProductDetailSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'title', 'category', 'price', 'count', 'description', 'rating', 'slug')

    def get_category(self, obj):
        return obj.category.title
