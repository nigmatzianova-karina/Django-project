from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    """
    Inline representation of CartItem objects for the Cart admin interface.
    Allows managing products within a specific cart directly from the Cart page.
    """
    model = CartItem
    extra = 0
    fields = ["product_display", "product", "quantity", "price_display", "total_price_display"]
    readonly_fields = ["product_display", "price_display", "total_price_display"]

    def product_display(self, obj):
        """
        Generates an HTML link to the product change page with its title and ID.
        """
        if obj and obj.product:
            url = reverse('admin:catalog_product_change', args=[obj.product.id])
            return format_html(
                '<a href="{}" target="_blank">{}</a><br>'
                '<small>Article: {}</small>',
                url, obj.product.title, obj.product.id
            )
        return "← Select a product on the right"

    product_display.short_description = "Current Product"

    def price_display(self, obj):
        """
        Displays the formatted unit price of the selected product.
        """
        if obj and obj.product:
            return f"{obj.product.price} RUB"
        return "-"

    price_display.short_description = "Unit Price"

    def total_price_display(self, obj):
        """
        Displays the formatted total price for the specific cart item position.
        """
        return f"{obj.total_price} RUB"

    total_price_display.short_description = "Subtotal"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Cart model.
    Provides detailed overview of user shopping carts, including totals and timestamps.
    """
    list_display = ["id", "user_display", "total_quantity", "total_price_display", "created_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["user__username", "user__email", "session_key"]
    inlines = [CartItemInline]

    def get_queryset(self, request):
        """
        Optimizes database performance by pre-fetching related user data.
        """
        return super().get_queryset(request).select_related('user')

    def user_display(self, obj):
        """
        Displays the user's full name and username, or session key for anonymous guests.
        """
        if obj.user:
            return f"{obj.user.get_full_name()} ({obj.user.username})"
        return f"Guest ({obj.session_key[:10]}...)"

    user_display.short_description = "Customer"

    def total_price_display(self, obj):
        """
        Displays the formatted total cost of all items in the cart.
        """
        return f"{obj.total_price} RUB"

    total_price_display.short_description = "Total Amount"
