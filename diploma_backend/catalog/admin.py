from django.contrib import admin
from django.utils import timezone
from .models import Product, Category, Review, Sale, Specification, ProductImage


class SpecificationInline(admin.TabularInline):
    """
    Inline editor for Product specifications.
    Displayed as a table within the Product admin page.
    """
    model = Specification
    extra = 3
    fields = ["id", "name", "value"]


class ProductImageInline(admin.TabularInline):
    """
    Inline editor for Product images.
    Allows uploading multiple images and setting the primary display photo.
    """
    model = ProductImage
    extra = 1
    fields = ["image", "alt", "is_main"]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin interface for product categories.
    Supports hierarchical structure and featured category highlights.
    """
    list_display = ["id", "title", "parent", "is_active", "is_featured"]
    list_filter = ["is_active", "is_featured"]
    search_fields = ["title"]
    list_editable = ["is_active", "is_featured"]
    list_select_related = ["parent"]
    ordering = ["title"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """
    Primary admin interface for Product management.
    Includes specifications, images, and basic catalog metadata.
    """
    list_display = ["id", "title", "category", "price", "is_active", "rating", "created_at"]
    list_filter = ["is_active", "category", "created_at"]
    search_fields = ["title", "description"]
    list_editable = ["price", "is_active"]
    list_select_related = ["category"]
    ordering = ["-created_at"]
    filter_horizontal = ['tags']
    inlines = [SpecificationInline, ProductImageInline]

    def get_queryset(self, request):
        """
        Optimizes the queryset by pre-fetching related tags to speed up rendering.
        """
        return super().get_queryset(request).prefetch_related('tags')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Moderation interface for product reviews.
    """
    list_display = ["id", "product", "author", "rate", "created_at"]
    list_filter = ["rate", "created_at"]
    search_fields = ["text", "product__title"]
    list_select_related = ["product"]


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    """
    Interface for managing promotional sales and discounts.
    Includes automated status tracking based on the current date.
    """
    list_display = ["id", "product", "sale_price", "date_from", "date_to", "is_active"]
    list_filter = ["date_from", "date_to"]
    search_fields = ["product__title"]
    list_select_related = ["product"]

    def is_active(self, obj):
        today = timezone.now().date()
        return obj.date_from <= today <= obj.date_to

    is_active.boolean = True
    is_active.short_description = 'Активна'
