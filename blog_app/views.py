from django.views.generic.list import ListView
from urllib import request
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView
from .forms import ArticleForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect, get_object_or_404

from .models import Article, Theme


class ArticleListView(ListView):
    model = Article
    context_object_name = 'articles'
    paginate_by = 8

    def get_context_data(self, **kwargs):
        paginator = Paginator(self.get_queryset(), self.paginate_by)
        page = self.request.GET.get('page')

        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)

        context = super().get_context_data(**kwargs)
        context['articles'] = articles
        context['themes'] = Theme.objects.all()
        return context


class ArticleThemeListView(View):

    def get(self, request, *args, **kwargs):
        theme_slug = kwargs.pop('slug', )
        theme = get_object_or_404(Theme, slug=theme_slug)
        articles = Article.objects.filter(theme=theme)
        title = theme.title

        context = {
            "articles": articles,
            "title": title,
        }

        return render(request, 'blog_app/article_list.html', context=context)


class ArticleDetailView(DetailView):
    model = Article

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.count_rating()
        self.object.save()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class CreateArticleView(LoginRequiredMixin, CreateView):
    template_name = 'blog_app/article_form.html'
    form_class = ArticleForm
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['articles'] = Article.objects.all()
        return context


class UpdateArticleView(LoginRequiredMixin, UpdateView):
    model = Article
    class_form = ArticleForm
    fields = ['slug', 'title', 'text', 'author', 'image', 'theme']
    success_url = '/blog/'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['articles'] = Article.objects.all()
        return context


