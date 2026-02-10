from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from orders.models import Order, OrderItem, DeliverySettings


class OrderItemInline(admin.TabularInline):
    """
    Displays individual products associated with an Order.
    Product details are read-only to preserve historical transaction data.
    """
    model = OrderItem
    extra = 0
    fields = ["product_link", "quantity", "price", "total_price_display"]
    readonly_fields = ["product_link", "quantity", "price", "total_price_display"]

    def product_link(self, obj):
        """Generates a clickable link to the product in the catalog."""
        if obj.product:
            url = reverse('admin:catalog_product_change', args=[obj.product.id])
            return format_html('<a href="{}">{}</a>', url, obj.product.title)  # Fixed: .title instead of .name
        return "N/A"

    product_link.short_description = "Product"

    def total_price_display(self, obj):
        """Calculates subtotal for this item line."""
        return f"{obj.price * obj.quantity} $"

    total_price_display.short_description = "Subtotal"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Administrative interface for Order processing.
    Provides filtering by status and payment type, and tracks delivery logistics.
    """
    list_display = ["id", "user", "delivery_type", "total_cost", "created_at"]
    list_filter = ["status", "delivery_type", "payment_type", "created_at"]
    search_fields = ["id", "full_name", "phone", "user__username"]
    ordering = ["-created_at"]
    inlines = [OrderItemInline]
    list_select_related = ["user"]


@admin.register(DeliverySettings)
class DeliverySettingsAdmin(admin.ModelAdmin):
    """
    Configuration for delivery prices and thresholds.
    """
    list_display = ["standard_delivery_cost", "express_delivery_surcharge", "free_delivery_threshold"]
