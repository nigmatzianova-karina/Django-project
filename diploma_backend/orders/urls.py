from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("orders", views.orders_view, name="orders"),
    path("orders/<int:id>", views.orders_by_id_view, name="order_by_id"),
]