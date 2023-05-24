from django import forms
from my_store_app.models import *
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.db.models import Count
import random


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Reviews
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(
                attrs={"class": "form-textarea", "placeholder": "Отзыв"}
            )
        }

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop("author", None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        review = super().save(commit=False)
        review.author = self.author
        if commit:
            review.save()
        return review


class SearchForm(forms.Form):
    keyword = forms.CharField(max_length=20, label="Искомое слово")
    products = forms.ModelChoiceField(
        queryset=Product.objects.all(), label="Товар", required=False
    )


class ProductFilterForm(forms.Form):
    expensive = forms.BooleanField(required=False)
    limited_edition = forms.BooleanField(required=False)
    min_price = forms.DecimalField(min_value=0, max_value=9999999999, required=False)
    max_price = forms.DecimalField(min_value=0, max_value=9999999999, required=False)
    tag = forms.ModelChoiceField(
        queryset=TagsFile.objects.all(),
        empty_label="Выберете тег с товарами",
        required=False,
    )
    count = forms.IntegerField(min_value=0, required=False, label="Количество товара")
