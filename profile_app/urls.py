from django.contrib import admin
from django.urls import include, path
from profile_app.views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = (
        [
            path("account/<int:profile_id>/", AboutMeView.as_view(), name="account"),
            path(
                "account/update/<int:profile_pk>/",
                UpdateProfile.as_view(),
                name="update_profile",
            ),
            path("register/", RegisterView.as_view(), name="register"),
            path("logout/", AuthorLogoutView.as_view(), name="logout"),
            path(
                "login/",
                Login.as_view(template_name="profile_app/login.html"),
                name="login",
            ),
            path("login-by-email", ReturnPasswordByEmail.as_view(), name="login-by-email"),
        ]
        + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
        + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
