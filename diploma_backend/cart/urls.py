from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("basket", views.basket_view, name="basket")
]
