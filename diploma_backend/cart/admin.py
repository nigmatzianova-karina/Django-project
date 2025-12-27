from django.contrib import admin
from django.utils.html import format_html

from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    fields = ["product_display", "product", "quantity", "price_display", "total_price_display"]
    readonly_fields = ["product_display", "price_display", "total_price_display"]

    def product_display(self, obj):
        """Отображение выбранного товара со ссылкой (только чтение)"""
        if obj and obj.product:
            url = f"/admin/catalog/product/{obj.product.id}/change/"
            return format_html(
                '<a href="{}" target="_blank">{}</a><br>'
                '<small>Артикул: {}</small>',
                url,
                obj.product.title,
                obj.product.id
            )
        return "← Выберите товар справа"

    product_display.short_description = "Текущий товар"

    def price_display(self, obj):
        """Отображение цены товара"""
        return f"{obj.product.price} руб."

    price_display.short_description = "Цена за единицу"

    def total_price_display(self, obj):
        """Отображение общей стоимости позиции"""
        return f"{obj.total_price} руб."

    total_price_display.short_description = "Общая стоимость"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ["id", "user_display", "total_quantity", "total_price", "created_at"]
    list_filter = ["created_at", "updated_at"]
    search_fields = ["user__username", "user__email", "session_key"]
    inlines = [CartItemInline]

    def user_display(self, obj):
        if obj.user:
            return f"{obj.user.get_full_name()} ({obj.user.username})"
        return f"Аноним ({obj.session_key[:10]}...)"

    user_display.short_description = "user_display"

    def total_quantity_display(self, obj):
        """Отображение общего количества товаров"""
        return obj.total_quantity

    total_quantity_display.short_description = "Кол-во товаров"

    def total_price_display(self, obj):
        """Отображение общей стоимости"""
        return f"{obj.total_price} руб."

    total_price_display.short_description = "Общая стоимость"
