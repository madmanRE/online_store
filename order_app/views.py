from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from my_store_app.models import *
from order_app.forms import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from my_store_app.mixins import CategoryMixin
from django.db.models import Count, Min, OuterRef, Subquery, Sum
from datetime import datetime, timedelta
from django.utils import timezone
from random import shuffle, choice
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic.edit import FormMixin, UpdateView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.db.models import Q
from django.views.generic import FormView
from django.contrib.auth.forms import AuthenticationForm
from collections import Counter, defaultdict
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_http_methods
from django.db import transaction
import os


class CartView(CategoryMixin, LoginRequiredMixin, TemplateView):
    """Просмотр корзины"""

    template_name = "order_app/cart.html"

    def get(self, request, *args, **kwargs):
        user = request.user.profile
        try:
            cart = Basket.objects.filter(username=user).first()
            items = cart.items.all()
            products = [item.product for item in items]
            counts = Counter(products)
            total_price = sum(
                item.product.price * item.product_quantity for item in items
            )
            categories = self.get_categories()
            context = {
                "products": products,
                "total_price": total_price,
                "counts": counts,
                "categories": categories,
                "quantities": [item.product_quantity for item in items],
                "items": items,
            }
        except Basket.DoesNotExist:
            cart = Basket.objects.create(username=user)
            context = {"products": [], "total_price": 0}

        except:
            context = {"products": [], "total_price": 0}

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Пост запрос на удаление товара из корзины"""
        user = request.user.profile
        product_id = request.POST.get("product_id")
        if product_id:
            product = Product.objects.get(id=product_id)
            cart = Basket.objects.filter(username=user).first()
            item = cart.items.filter(product=product).first()
            quantity = int(request.POST.get("amount", 1))
            if item:
                item.delete()
            return redirect("cart")
        return super().post(request, *args, **kwargs)


@login_required
def add_to_cart(request, product_id):
    """Добавление товара в корзину из карточки товара"""
    user_profile = request.user.profile if request.user.is_authenticated else None
    if not user_profile:
        return redirect("login")
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get("quantity", 1))
    cart, created = Basket.objects.get_or_create(username=user_profile)

    product_in_cart, created = BasketItem.objects.get_or_create(
        product=product, basket=cart, defaults={"product_quantity": quantity}
    )
    if not created:
        product_in_cart.product_quantity += quantity
        product_in_cart.save()

    return redirect("cart")


class OrderingPageView(CategoryMixin, LoginRequiredMixin, View):
    """Просмотр страницы заказа"""

    template_name = "order_app/order.html"

    def get(self, request, *args, **kwargs):
        print("get")
        card_form = CardForm()
        code_form = CodeForm()
        user = request.user.profile
        basket = Basket.objects.filter(username=user).first()

        order_history_id = request.session.get("order_history")
        if order_history_id is not None:
            order_history = OrderHistory.objects.filter(id=order_history_id).first()
        else:
            order_history = OrderHistory.objects.create(
                user_order=user,
                total_cost=basket.total_cost(),
                delivery_type=request.GET.get("delivery", "не указан"),
                payment_type=request.GET.get("pay", "не указан"),
                city=request.GET.get("city", "не указан"),
                address=request.GET.get("address", "не указан"),
            )
            request.session["order_history"] = order_history.id

        context = {
            "categories": self.get_categories(),
            "user": user,
            "basket": basket,
            "order_history": order_history,
            "card_form": card_form,
            "code_form": code_form,
        }

        if request.user.profile.basket.count_products() > 0:
            return render(request, self.template_name, context)
        else:
            return redirect("catalog")

    def post(self, request, *args, **kwargs):
        print("post")
        user = request.user.profile if request.user.is_authenticated else None
        if not user:
            messages.error(
                request, "Для оформления заказа вам необходимо войти в систему"
            )
            return redirect("login")

        basket = Basket.objects.filter(username=user).first()
        order_history = OrderHistory.objects.filter(
            user_order=user, confirmed=False
        ).last()

        if user.balance >= basket.total_cost():
            available_products = []
            ordered_products = []

            order_history.delivery_type = request.POST.get("delivery", "не указан")
            order_history.payment_type = request.POST.get("pay", "не указан")
            order_history.status = "не указан"
            order_history.city = request.POST.get("city", "не указан")
            order_history.address = request.POST.get("address", "не указан")
            order_history.save()

            for prod in basket.items.all():
                if prod.product_quantity <= prod.product.count:
                    prod.product.count -= prod.product_quantity
                    prod.product.rating += 1
                    prod.product.save()
                    available_products.append(prod.product)
                    ordered_product = OrderedProduct(
                        product=prod.product, quantity=prod.product_quantity
                    )
                    ordered_product.order = order_history
                    ordered_products.append(ordered_product)
                else:
                    return HttpResponse("Недостаточно товара на складе")

            OrderedProduct.objects.bulk_create(ordered_products)

            Product.objects.bulk_update(available_products, ["count"])

            available_products = []
            ordered_products = []
            for prod in basket.items.all():
                if prod.product_quantity <= prod.product.count:
                    prod.product.count -= prod.product_quantity
                    prod.product.save()
                    available_products.append(prod.product)
                    ordered_products.append(
                        OrderedProduct(
                            product=prod.product,
                            quantity=prod.product_quantity,
                            order=order_history,
                        )
                    )
                else:
                    return HttpResponse("<h2>Недостаточно товара на складе</h2>")

            Product.objects.bulk_update(available_products, ["count"])
            order_history.product_order.set(available_products)

            Order.objects.create(current_basket=basket, free_delivery=False)

            if order_history.delivery_type == "express":
                if user.balance >= 500 + basket.total_cost():
                    order_history.total_cost += 500
                    order_history.status = "Оплачено"
                    order_history.confirmed = True
                    order_history.save()
                    user.balance -= basket.total_cost()
                    user.balance -= 500
                    user.save()
                    basket.items.all().delete()
                    request.session.modified = True
                    del request.session["order_history"]
                    return redirect("index")
                else:
                    return HttpResponse(
                        "<h2>Недостаточно средств на балансе, "
                        "воспользуйтесь обычной доставкой или "
                        f'положите на счет еще <span style="color:red">{500 + basket.total_cost() - user.balance}</span> рублей.</h2>'
                    )
            else:
                order_history.status = "Оплачено"
                order_history.confirmed = True
                order_history.save()
                user.balance -= basket.total_cost()
                user.save()
                basket.items.all().delete()
                request.session.modified = True
                del request.session["order_history"]
                return redirect("index")

        else:
            return HttpResponse("Недостаточно средств на балансе")


class FinishOrderHistory(CategoryMixin, View):
    """Можно использовать класс для оплаты.
    Данный класс пока не используется,
    возможно будет смысл прикрутить его позже"""

    template_name = "order_app/payment.html"

    def get(self, request, *args, **kwargs):
        card_form = CardForm()
        code_form = CodeForm()
        user = request.user.profile if request.user.is_authenticated else None
        basket = Basket.objects.filter(username=user).first()
        order_history = OrderHistory.objects.filter(
            user_order=user, confirmed=False
        ).last()

        context = {
            "categories": self.get_categories(),
            "user": user,
            "basket": basket,
            "order_history": order_history,
            "card_form": card_form,
            "code_form": code_form,
        }

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        user = request.user.profile if request.user.is_authenticated else None
        basket = Basket.objects.filter(username=user).first()
        order_history = OrderHistory.objects.filter(
            user_order=user, confirmed=False
        ).last()
        form = ""
        if "card_form" in request.POST:
            form = CardForm(request.POST)
        else:
            form = CodeForm(request.POST)
        if form.is_valid():
            if order_history.delivery_type == "express":
                if user.balance >= 500 + basket.total_cost():
                    order_history.total_cost += 500
                    order_history.status = "Оплачено"
                    order_history.confirmed = True
                    order_history.save()
                    user.balance -= basket.total_cost()
                    user.balance -= 500
                    user.save()
                    basket.items.all().delete()
                    request.session.modified = True
                    del request.session["order_history"]
                    return redirect("index")
                else:
                    return HttpResponse(
                        "<h2>Недостаточно средств на балансе, "
                        "воспользуйтесь обычной доставкой или "
                        f'положите на счет еще <span style="color:red">{500 + basket.total_cost() - user.balance}</span> рублей.</h2>'
                    )
            else:
                order_history.status = "Оплачено"
                order_history.confirmed = True
                order_history.save()
                user.balance -= basket.total_cost()
                user.save()
                basket.items.all().delete()
                request.session.modified = True
                del request.session["order_history"]
                return redirect("index")
        else:
            return HttpResponse("Недостаточно средств на балансе")


class OrderHistoryView(CategoryMixin, LoginRequiredMixin, View):
    """Просмотр истории заказов"""

    template_name = "order_app/historyorder.html"

    def get(self, request, *args, **kwargs):
        user = request.user.profile
        basket = Basket.objects.filter(username=user).first()
        history = OrderHistory.objects.filter(user_order=user).order_by(
            "-payment_date", "-pk"
        )
        orders = Order.objects.filter(current_basket__username=user)
        context = {
            "categories": self.get_categories(),
            "user": user,
            "basket": basket,
            "history": history,
            "orders": orders,
            "order_id": kwargs.get("order_id"),
        }

        return render(request, self.template_name, context)


class OneOrderView(CategoryMixin, LoginRequiredMixin, View):
    """Просмотр одного заказа"""

    template_name = "order_app/oneorder.html"
    pk_url_kwarg = "order_id"

    def get_object(self):
        user = self.request.user.profile
        return get_object_or_404(OrderHistory, pk=self.kwargs.get("hist_id"))

    def get(self, request, *args, **kwargs):
        user = request.user.profile
        basket = Basket.objects.filter(username=user).first()
        hist = self.get_object()
        products = hist.products.all()

        context = {
            "categories": self.get_categories(),
            "user": user,
            "basket": basket,
            "hist": hist,
            "products": products,
        }

        return render(request, self.template_name, context)
