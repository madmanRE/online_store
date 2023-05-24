from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from my_store_app.models import *
from my_store_app.forms import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .mixins import CategoryMixin
from django.db.models import Count, Min, OuterRef, Subquery, Sum
from datetime import datetime
from random import choice
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
import os
from blog_app.models import Article, Theme


class CategoryView(CategoryMixin, View):
    """Формирование списка категорий, популярных товаров,
    лимитированных, баннеров и путей до изображений этих категорий"""

    def get(self, request):
        category = self.get_categories()
        slider_product = Product.objects.all().order_by("-price")[:6]
        popular_product = Product.objects.all().order_by("-reviews")[:8]
        limited_edition = Product.objects.filter(limited_edition=True).order_by(
            "price"
        )[:20]

        banners = (
            CategoryProduct.objects.filter(product__in=popular_product)
            .annotate(num_products=Count("product"), min_price=Min("product__price"))
            .order_by("-num_products")[0:3]
        )

        for banner in banners:
            products = banner.product_set.all()
            banner.min_price = products.aggregate(Min("price"))["price__min"]

        limited_offers = LimitedOffer.objects.all()
        limited_offer = choice(limited_offers)
        duration = limited_offer.duration
        now = datetime.now() + duration
        now_str = now.strftime("%d.%m.%Y %H:%M")

        return render(
            request,
            "my_store_app/index.html",
            {
                "categories": category,
                "popular_product": popular_product,
                "limited_edition": limited_edition,
                "banners": banners,
                "slider_product": slider_product,
                "limited_offer": limited_offer,
                "now": now_str,
            },
        )


class CatalogView(CategoryMixin, ListView):
    """На сайте отображается каталог товаров с возможностью фильтрации,
    сортировки и постраничной навигации"""

    paginate_by = 8

    def get(self, request):
        category = self.get_categories()
        products = Product.objects.all()

        all_tags = TagsFile.objects.all()

        tag_param = request.GET.get("tags")

        if tag_param == "all":
            tags = all_tags
        elif tag_param == "hide":
            tags = set()
            for prod in products:
                for tag in prod.tags.all():
                    tags.add(tag)
            return redirect(request.path_info)
        else:
            tags = set()
            for prod in products:
                for tag in prod.tags.all():
                    tags.add(tag)

        title = "Каталог товаров"

        sort_param = request.GET.get("sort_by", None)

        if sort_param == "price":
            products = products.order_by("price")
        elif sort_param == "reviews":
            products = products.order_by("-reviews", "-rating")
        elif sort_param == "date":
            products = products.order_by("-date")
        elif sort_param == "reviews_count":
            products = Product.objects.annotate(
                num_reviews=Count("product_title_product_set")
            ).order_by("-num_reviews")
        else:
            products = products.order_by().order_by("-price")

        paginator = Paginator(products, self.paginate_by)
        page = request.GET.get("page")

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        context = {
            "categories": category,
            "products": products,
            "tags": tags,
            "title": title,
            "page_obj": products,
        }
        return render(request, "my_store_app/catalog.html", context=context)


def product_filter(request):
    paginate_by = 8
    form = ProductFilterForm(request.GET)
    products = Product.objects.all()

    if form.is_valid():
        expensive = form.cleaned_data.get("expensive")
        tag = form.cleaned_data.get("tag")
        min_price = form.cleaned_data.get("min_price")
        max_price = form.cleaned_data.get("max_price")
        count = form.cleaned_data.get("count")
        limited = form.cleaned_data.get("limited_edition")

        if tag:
            try:
                tag_obj = TagsFile.objects.get(tags_name=tag)
                print(tag_obj)
                products = tag_obj.tags.all()
                for i in products:
                    for j in i.tags.all():
                        print(j)
            except TagsFile.DoesNotExist:
                products = Product.objects.none()
        if expensive:
            products = products.filter(price__gte=400000)
        if limited:
            products = products.filter(limited_edition=True)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
        if count:
            products = products.filter(count__gte=count)

    paginator = Paginator(products, paginate_by)
    page = request.GET.get("page")

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    context = {"products": products, "form": form, "page_obj": products}
    return render(request, "my_store_app/catalog.html", context)


class ProductDetailView(CategoryMixin, DetailView):
    """Отображение карточки товара на сайте"""

    def get(self, request, *args, **kwargs):
        categories = self.get_categories
        product_slug = kwargs.get("product_slug")
        product = get_object_or_404(Product, slug=product_slug)
        specifications = Specifications.objects.filter(product=product)
        reviews = Reviews.objects.filter(product=product)
        reviews_count = Reviews.objects.filter(product=product).count()
        form = ReviewForm(author=request.user)
        gallery = ProductImage.objects.filter(product_ref=product)
        product.upper_reviews_product()

        context = {
            "product": product,
            "categories": categories,
            "specifications": specifications,
            "reviews": reviews,
            "reviews_count": reviews_count,
            "form": form,
            "gallery": gallery,
        }
        return render(request, "my_store_app/product.html", context)

    def post(self, request, *args, **kwargs):
        product_slug = kwargs.get("product_slug")
        user = None
        try:
            user = request.user.profile
        except:
            pass
        product = get_object_or_404(Product, slug=product_slug)
        form = ReviewForm(request.POST, author=request.user.profile)
        if form.is_valid():
            form.instance.product = product
            form.save()
            return HttpResponseRedirect(reverse("product", args=[product_slug]))
        else:
            categories = self.get_categories
            specifications = Specifications.objects.filter(product=product)
            reviews = Reviews.objects.filter(product=product)
            reviews_count = Reviews.objects.filter(product=product).count()
            context = {
                "product": product,
                "categories": categories,
                "specifications": specifications,
                "reviews": reviews,
                "reviews_count": reviews_count,
                "form": form,
                "user": user,
            }
            return render(request, "my_store_app/product.html", context)


class CategoryDetailView(CategoryMixin, View):
    """Отображение категорий на сайте. Аналогично каталогу,
    но в запрос попадают только товары из конкретной категории
    и теги, принаждлежащие только данной категории."""

    paginate_by = 8

    def get(self, request, *args, **kwargs):
        categories = self.get_categories()
        category_slug = kwargs.get("category_slug")
        category = get_object_or_404(CategoryProduct, slug=category_slug)
        products = Product.objects.filter(category=category)

        all_tags = TagsFile.objects.filter(tags_in_category=category)

        tag_param = request.GET.get("tags")

        if tag_param == "all":
            tags = all_tags
        elif tag_param == "hide":
            tags = set()
            for prod in products:
                for tag in prod.tags.all():
                    tags.add(tag)
            return redirect(request.path_info)
        else:
            tags = set()
            for prod in products:
                for tag in prod.tags.all():
                    tags.add(tag)

        sort_param = request.GET.get("sort_by", None)

        if sort_param == "price":
            products = products.order_by("price")
        elif sort_param == "reviews":
            products = products.order_by("-reviews", "-rating")
        elif sort_param == "date":
            products = products.order_by("-date")
        elif sort_param == "reviews_count":
            products = Product.objects.annotate(
                num_reviews=Count("product_title_product_set")
            ).order_by("-num_reviews")
        else:
            products = products.order_by().order_by("-price")

        paginator = Paginator(products, self.paginate_by)
        page = request.GET.get("page")

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        context = {
            "categories": categories,
            "category": category,
            "products": products,
            "tags": tags,
            "page_obj": products,
        }
        return render(request, "my_store_app/catalog.html", context=context)


class TagPageView(CategoryMixin, View):
    """Теговая страница"""

    paginate_by = 8

    def get(self, request, *args, **kwargs):
        categories = self.get_categories()
        tag_id = kwargs.get("tag_id")
        tag = get_object_or_404(TagsFile, id=tag_id)
        products = Product.objects.filter(tags=tag)
        title = tag.tags_name

        sort_param = request.GET.get("sort_by", None)

        if sort_param == "price":
            products = products.order_by("price")
        elif sort_param == "reviews":
            products = products.order_by("-reviews", "-rating")
        elif sort_param == "date":
            products = products.order_by("-date")
        elif sort_param == "reviews_count":
            products = Product.objects.annotate(
                num_reviews=Count("product_title_product_set")
            ).order_by("-num_reviews")
        else:
            products = products.order_by().order_by("-price")

        paginator = Paginator(products, self.paginate_by)
        page = request.GET.get("page")

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        context = {
            "categories": categories,
            "products": products,
            "page_obj": products,
            "title": title,
        }
        return render(request, "my_store_app/catalog.html", context=context)


def search(request):
    def get_categories(*args, **kwargs):
        data = CategoryProduct.objects.all()
        file_name_list = []
        for image in data:
            file = os.path.basename(str(image.image))
            file_name_list.append(file)

        category = zip(data, file_name_list)
        return category

    categories = get_categories()

    if request.method == "POST":
        sf = SearchForm(request.POST)
        if sf.is_valid():
            keyword = sf.cleaned_data["keyword"]
            products = Product.objects.filter(
                Q(title__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(tags__tags_name__icontains=keyword)
            ).distinct()

            articles = Article.objects.filter(
                Q(title__icontains=keyword)
                | Q(text__icontains=keyword)
                | Q(theme__title__icontains=keyword)
            ).distinct()

            context = {"products": products, "articles":articles, "form": sf, "categories": categories}
            return render(request, "my_store_app/search.html", context)
        else:
            message = "Невалидный запрос, попробуйте выполнить поиск снова"
            context = {
                "invalid": message,
                "categories": categories,
            }
            return render(request, "my_store_app/search.html", context)

    else:
        sf = SearchForm()
    context = {"form": sf, "categories": categories}
    return render(request, "my_store_app/search.html", context)


class AboutUsView(CategoryMixin, View):
    def get(self, request, *args, **kwargs):
        categories = self.get_categories()
        context = {"categories": categories}
        return render(request, "my_store_app/about.html", context)


def api_view(request):
    return render(request, "my_store_app/api.html")