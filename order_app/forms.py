from django import forms
from my_store_app.models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.db.models import Count
from .services import validate_card
import random


class CardForm(forms.Form):
    card_number = forms.CharField(
        label="Номер карты",
        max_length=8,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def clean_card_number(self):
        card_number = self.cleaned_data["card_number"]
        if len(card_number) > 8:
            raise forms.ValidationError(
                "Номер карты должен состоять из не более 8 цифр"
            )
        if not validate_card(card_number):
            raise forms.ValidationError(
                "Номер карты должен быть четным и не оканчиваться на 0"
            )
        return card_number


class CodeForm(forms.Form):
    code = forms.CharField(
        label="Сгенерированный код",
        max_length=8,
        widget=forms.TextInput(attrs={"class": "form-control", "readonly": "readonly"}),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get("code"):
            self.initial["code"] = "".join(
                [str(random.randint(0, 9)) for _ in range(8)]
            )

    def clean_code(self):
        card_number = self.cleaned_data["code"]
        if len(card_number) > 8:
            raise forms.ValidationError(
                "Номер карты должен состоять из не более 8 цифр"
            )
        if not validate_card(card_number):
            raise forms.ValidationError(
                "Номер карты должен быть четным и не оканчиваться на 0"
            )
        return card_number
