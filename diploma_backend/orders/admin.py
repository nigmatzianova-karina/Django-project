from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from orders.models import Order, OrderItem, DeliverySettings


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ["product_link", "quantity", "price", "total_price"]
    readonly_fields = ["product_link", "quantity", "price", "total_price"]

    def product_link(self, obj):
        if obj.product:
            url = reverse('admin:catalog_product_change', args=[obj.product.id])
            return format_html('<a href="{}">{}</a>', url, obj.product.name)
        return "-"
    product_link.short_description = "Товар"

    def total_price(self, obj):
        return f"{obj.price * obj.quantity} $"
    total_price.short_description = "Сумма"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "order_number", "status", "address", "phone", "total_cost"]
    list_filter = ["status", "delivery_type", "payment_type", "payment_status", "created_at"]
    search_fields = ["order_number", "full_name", "phone", "address", "status"]
    ordering = ["-created_at"]
    inlines = [OrderItemInline]