from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path('categories/', views.categories_view, name='categories'),
    path("catalog/", views.catalog_view, name="catalog"),
    path("sales/", views.sales_view, name="sales"),
    path("tags/", views.tags_view, name="tags"),
    path("banners/", views.banners_view, name="banners"),

    path("products/limited/", views.limited_products_view, name="limited_products"),
    path("products/popular/", views.popular_products_view, name="popular_products"),
    path(f"product/<int:id>/", views.products_by_id_view, name="product_by_id"),
    path(f"product/<int:id>/reviews", views.products_reviews_view, name="product_review"),
]
