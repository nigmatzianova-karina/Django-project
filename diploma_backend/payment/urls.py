from django.urls import path
from . import views

app_name = "payment"

urlpatterns = [
    path("payment/<int:id>", views.payment_view, name="payment"),
    path("payment-someone/<int:id>/", views.payment_someone_view, name="payment-someone")
]