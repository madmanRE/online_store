from django.contrib import admin
from django.urls import include, path
from blog_app.views import *
from .views import *
from django.conf import settings
from django.conf.urls.static import static

app_name = 'api'

urlpatterns = (
        [
            path('articles/<int:pk>', ArticleDetailView.as_view(), name='article_api'),
            path('articles/', ArticleListView.as_view(), name='articles_api'),
            path('products/', ProductListApiView.as_view(), name='products_api'),
        ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
