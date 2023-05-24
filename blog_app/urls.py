from django.contrib import admin
from django.urls import include, path
from blog_app.views import *
from django.conf import settings
from django.conf.urls.static import static
from .views import CreateArticleView, ArticleListView, ArticleDetailView, ArticleThemeListView, UpdateArticleView

app_name = 'blog_app'

urlpatterns = [
                  path('update_article/<int:pk>/', UpdateArticleView.as_view(), name='update_article'),
                  path('theme/<slug:slug>/', ArticleThemeListView.as_view(), name='theme'),
                  path('create_article/', CreateArticleView.as_view(), name='create_article'),
                  path('', ArticleListView.as_view(), name='blog'),
                  path('<slug:slug>/', ArticleDetailView.as_view(), name='article'),

              ] \
              + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
