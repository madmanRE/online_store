from django.contrib import admin
from .models import *


class ThemeAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'count']

    def count(self, obj):
        return obj.count_articles()


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'shorts', 'slug', 'theme', 'author', 'date', 'rating']
    search_fields = ('title', 'text',)

    def shorts(self, obj):
        return obj.text[0:50] + "..."


admin.site.register(Theme, ThemeAdmin)
admin.site.register(Article, ArticleAdmin)