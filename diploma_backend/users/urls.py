from django.urls import path
from . import views

app_name="users"

urlpatterns = [
    path("profile", views.profile_view, name="profile"),
    path("profile/avatar", views.profile_avatar_view, name="profile_avatar"),
    path("profile/password", views.profile_password_view, name="profile_password"),

    path("sign-in", views.sign_in_view, name="sign-in"),
    path("sign-up", views.sign_up_view, name="sign-up"),
    path("sign-out", views.sign_out_view, name="sign-out")
]
