from django.contrib import admin
from my_store_app.models import *


class UserProfileAdmin(admin.ModelAdmin):
    list_display = [
        "username",
        "email",
    ]
    search_fields = ["email"]


admin.site.register(Profile, UserProfileAdmin)
