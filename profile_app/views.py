from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, CreateView
from my_store_app.models import *
from .forms import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LogoutView, LoginView
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from my_store_app.mixins import CategoryMixin
from django.db.models import Sum
from django.views.generic.edit import UpdateView
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views.generic import FormView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt


class RegisterView(CategoryMixin, View):
    """Класс регистрации нового пользователя"""

    def get(self, request):
        categories = self.get_categories()
        form = AuthorRegisterForm()
        return render(
            request,
            "profile_app/registr.html",
            {"form": form, "categories": categories},
        )

    def post(self, request):
        form = AuthorRegisterForm(request.POST)
        form.fields["phone"].required = False
        if form.is_valid():
            full_name = form.cleaned_data.get("full_name")
            phone = form.cleaned_data.get("phone")
            email = form.cleaned_data.get("email")
            raw_password = form.cleaned_data.get("password")
            username = form.cleaned_data.get("login")
            try:
                user = User.objects.create_user(
                    username=username, first_name=full_name, email=email
                )
                user.set_password(raw_password)
                user.save()
                login(request, user)
                profile = Profile.objects.create(
                    user=user,
                    username=username,
                    full_name=full_name,
                    phone=phone,
                    email=email,
                )
                basket = Basket.objects.create(username=profile)
                profile.basket = basket
                profile.save()
                return redirect("/")
            except IntegrityError:
                form.add_error("login", "Пользователь с таким логином уже существует")

        return render(request, "profile_app/registr.html", {"form": form})


class AuthorLogoutView(LogoutView):  # +
    """Выход из учетной записи"""

    next_page = "/"


class Login(CategoryMixin, FormView):
    template_name = "profile_app/login.html"
    form_class = AuthenticationForm
    success_url = "/"

    def form_valid(self, form):
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            return redirect(self.success_url)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["categories"] = self.get_categories()
        return context


def save_email(email):
    email = f'{str(email.body)}\nАдресат:{str(email.to)}\n\n'
    with open('email_log.txt', 'a', encoding='utf-8') as log:
        log.write(email)


class ReturnPasswordByEmail(CategoryMixin, TemplateView):
    template_name = "profile_app/e-mail.html"

    def get_context_data(self, **kwargs):
        categories = self.get_categories()
        context = super().get_context_data(**kwargs)
        context["categories"] = categories
        return context

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        form = PasswordEmailRecoveryForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                messages.error(request, "Пользователь с указанным адресом электронной почты не существует.")
                return redirect("login-by-email")

            email_subject = 'Восстановление пароля магазин Megano'
            email_body = f'Ваш пароль: {user.password}'
            email = EmailMessage(
                subject=email_subject,
                body=email_body,
                to=[email]
            )
            # email.send()
            save_email(email)

            messages.success(request,
                             "Письмо с инструкциями по восстановлению пароля отправлено на вашу электронную почту.")
            return redirect("login-by-email")
        else:
            pass

        return render(request, self.template_name, {"form": form})


class AboutMeView(CategoryMixin, LoginRequiredMixin, TemplateView):
    """Переход в личный кабинет"""

    template_name = "profile_app/account.html"

    def get_context_data(self, **kwargs):
        categories = self.get_categories()
        user_profile = self.request.user.profile
        try:
            cart = Basket.objects.get(username=user_profile)
        except Basket.DoesNotExist:
            cart = Basket.objects.create(username=user_profile)
        items = cart.items.all()
        total_price = items.aggregate(Sum("product__price"))["product__price__sum"] or 0
        last_orders = OrderHistory.objects.filter(user_order=user_profile).order_by(
            "-payment_date", "-id"
        )[:3]
        context = super().get_context_data(**kwargs)
        context["user"] = user_profile
        context["total_price"] = total_price
        context["categories"] = categories
        context["items"] = items
        context["last_orders"] = last_orders
        return context


class UpdateProfile(CategoryMixin, UpdateView):
    """Редактирование профиля"""

    model = Profile
    form_class = ProfileForm
    template_name = "profile_app/profile.html"

    def get_object(self, queryset=None):
        return self.model.objects.get(pk=self.kwargs["profile_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = self.get_categories()
        context["categories"] = categories
        return context

    def form_valid(self, form):
        user = self.request.user
        new_password = form.cleaned_data.get("password")
        if new_password:
            user.set_password(new_password)
            user.save()

        response = super().form_valid(form)

        user = authenticate(username=user.username, password=new_password)
        if user is not None:
            login(self.request, user)

        return response

    def get_success_url(self):
        return reverse_lazy(
            "account", kwargs={"profile_id": self.request.user.profile.pk}
        )
