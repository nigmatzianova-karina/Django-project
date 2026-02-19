from datetime import datetime
from django.conf import settings
from django.db import models
from django.db.models import Sum, F
from catalog.models import Product


class Cart(models.Model):
    """
    Represents a shopping cart assigned to either a registered User or an anonymous Session.

    Attributes:
        user (User): Optional reference to the authenticated user.
        session_key (str): Unique identifier for anonymous guest carts.
        created_at (datetime): Timestamp when the cart was initialized.
        updated_at (datetime): Timestamp of the last modification (items added/removed).
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="cart",
                                null=True, blank=True, verbose_name="Пользователь")
    session_key = models.CharField(max_length=255, blank=True, null=True, db_index=True, verbose_name="Ключ сессии")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = 'Корзины'
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"Cart for user {self.user.username}"
        return f"Guest Cart {self.session_key[:10]}..."

    @property
    def total_quantity(self):
        """
        Calculates the sum of all item quantities in the cart using database aggregation.
        """
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0

    @property
    def total_price(self):
        """
        Calculates the total cost of all products in the cart.
        Multiplies quantity by price for each item at the database level.
        """
        result = self.items.aggregate(
            total=Sum(F('quantity') * F('product__price'), output_field=models.DecimalField())
        )
        return result['total'] or 0


class CartItem(models.Model):
    """
    Represents an individual product entry within a shopping cart.

    Attributes:
        cart (Cart): The parent cart container.
        product (Product): The item added to the cart.
        quantity (int): Number of units for this product.
        added_at (datetime): Timestamp when the product was added.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items", verbose_name="Корзина")
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
        """
        Returns the calculated price for this position (Unit Price * Quantity).
        """
        return self.product.price * self.quantity

    def save(self, *args, **kwargs):
        """
        Custom save method to trigger the parent Cart's updated_at timestamp.
        """
        super().save(*args, **kwargs)
        if self.cart:
            self.cart.save(update_fields=['updated_at'])


class SessionCart:
    """
    A lightweight shopping cart manager for unauthorized users that stores data in request.session.
    """
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('cart')
        if not cart:
            cart = self.session['cart'] = {}
        self.cart = cart

    def add(self, product_id, quantity):
        p_id = str(product_id)
        if p_id not in self.cart:
            self.cart[p_id] = {
                'quantity': 0,
                'added_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%S%z')
            }
        self.cart[p_id]['quantity'] += quantity
        self.save()

    def remove(self, product_id, quantity):
        p_id = str(product_id)
        if p_id in self.cart:
            self.cart[p_id]['quantity'] -= quantity
            if self.cart[p_id]['quantity'] <= 0:
                del self.cart[p_id]
            self.save()

    def save(self):
        self.session.modified = True

    @property
    def items_data(self):
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids).select_related('category').prefetch_related('images',
                                                                                                          'tags')

        results = []
        for product in products:
            item_info = self.cart[str(product.id)]
            results.append(type('Struct', (object,), {
                'product': product,
                'quantity': item_info['quantity'],
                'added_at': item_info['added_at']
            }))
        return results
