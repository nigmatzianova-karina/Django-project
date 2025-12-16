from django.conf import settings
from django.db import models

from catalog.models import Product


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart",
                                null=True, blank=True, verbose_name="Пользователь")
    session_key = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ключ сессии")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"Корзина пользователя {self.user.username}"
        return f"Корзина сессии {self.session_key[:10]}..."

    @property
    def total_quantity(self):
        """Общее количество товаров в корзине"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Общая стоимость корзины"""
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,related_name="items", verbose_name="Корзина")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    quantity = models.PositiveIntegerField(default=1, verbose_name='Количество')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = 'Товар в корзине'
        verbose_name_plural = 'Товары в корзине'
        unique_together = ['cart', 'product']
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.product.title} x{self.quantity}"

    @property
    def total_price(self):
        """Общая стоимость этого товара (цена × количество)"""
        return self.product.price * self.quantity

    def save(self, *args, **kwargs):
        """Обновляем updated_at корзины при изменении товаров"""
        super().save(*args, **kwargs)
        if self.cart:
            self.cart.save()
