from django.contrib import admin
from django.utils import timezone

from .models import Product, Category, Review, Sale, Specification, ProductImage


class SpecificationInline(admin.TabularInline):
    model = Specification
    extra = 3
    fields = ["id", "name"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image", "alt", "is_main"]


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'alt', 'is_main']
    list_filter = ['product', 'is_main']
    search_fields = ['product__title', 'alt']
    list_editable = ['is_main']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "parent", "is_active", "is_featured"]
    list_filter = ["is_active", "is_featured"]
    search_fields = ["title"]
    list_editable = ["is_active", "is_featured"]
    ordering = ["title"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "category", "price", "is_active", "rating", "created_at"]
    list_filter = ["is_active", "category", "created_at"]
    search_fields = ["title", "description"]
    list_editable = ["price", "is_active"]
    ordering = ["-created_at"]
    filter_horizontal = ['tags']
    inlines = [SpecificationInline, ProductImageInline]


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "author", "rate", "created_at"]
    list_filter = ["rate", "created_at"]
    search_fields = ["text", "product__title"]


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ["id", "product", "sale_price", "date_from", "date_to", "is_active"]
    list_filter = ["date_from", "date_to"]
    search_fields = ["product__title"]

    def is_active(self, obj):
        today = timezone.now().date()
        return obj.date_from <= today <= obj.date_to

    is_active.boolean = True
    is_active.short_description = 'Активна'
