from django import forms
from my_store_app.models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.db.models import Count
import random
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import EmailMessage


class AuthorRegisterForm(forms.Form):
    full_name = forms.CharField(required=True, help_text="имя пользователя")
    phone = forms.CharField(required=True, help_text="номер телефона")
    email = forms.EmailField(required=True, help_text="email")
    login = forms.CharField(required=True, help_text="логин")
    password = forms.CharField(required=True, help_text="пароль")


class ProfileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = Profile
        fields = [
            "username",
            "full_name",
            "phone",
            "email",
            "avatar",
            "balance",
            "password",
        ]

    def save(self, commit=True):
        profile = super(ProfileForm, self).save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            profile.user.set_password(password)
            profile.user.save()
        if commit:
            profile.save()
        return profile


class PasswordEmailRecoveryForm(forms.Form):
    email = forms.EmailField(label="E-mail")

    def send_password_email(self):
        email = self.cleaned_data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(self.request, "Пользователь с указанным адресом электронной почты не существует.")
            return redirect("login-by-email")

        email_subject = 'Восстановление пароля магазин Megano'
        email_body = f'Ваш пароль: {user.password}'
        email = EmailMessage(
            subject=email_subject,
            body=email_body,
            to=[email]
        )
        email.send()

        messages.success(self.request,
                         "Письмо с инструкциями по восстановлению пароля отправлено на вашу электронную почту.")
        return redirect("login-by-email")

