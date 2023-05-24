from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import os


class CategoryMixin:
    def get_categories(self):
        date = CategoryProduct.objects.all()
        file_name_list = []
        for image in date:
            file = os.path.basename(str(image.image))
            file_name_list.append(file)

        category = zip(date, file_name_list)
        return category
