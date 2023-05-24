from django.forms import ModelForm
from django import forms
from .models import Article

class ArticleForm(ModelForm):
    class Meta:
        model = Article
        fields = (
            'title',
            'text',
            'author',
            'slug',
            'image',
            'theme',
        )

