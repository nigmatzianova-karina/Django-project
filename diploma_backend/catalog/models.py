from django.conf import settings
from django.db import models
from django.db.models import Avg
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


class Category(models.Model):
    """
    Represent a product category with support for hierarchical (parent-child) relationships.
    """
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='categories/', blank=True, null=True, default='categories/placeholder.jpg')
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_featured = models.IntegerField(default=0, help_text="Ranking for featured display on home page")

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']


class Tag(models.Model):
    """
    Simple label for product categorization and filtering.
    """
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Product(models.Model):
    """
    The central entity representing an item in the store catalog.
    Includes inventory tracking, banner metadata, and rating cache.
    """
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    full_description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.PositiveIntegerField(default=0, verbose_name="Stock count")
    limited_edition = models.BooleanField(default=False)
    free_delivery = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rating = models.FloatField(default=0.0, help_text="Cached average rating from reviews")
    is_banner = models.BooleanField(default=False)
    banner_order = models.IntegerField(default=0)
    banner_text = models.TextField(blank=True)
    sort_index = models.IntegerField(default=0, verbose_name="Индекс сортировки")
    purchases_count = models.PositiveIntegerField(default=0, verbose_name="Количество покупок")

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    tags = models.ManyToManyField(Tag, blank=True)

    @property
    def reviews_count(self):
        """Returns total number of reviews. Warning: triggers SQL COUNT."""
        return self.reviews.count()

    def update_rating(self):
        """
        Calculates and saves the average rating from all associated reviews.
        Returns the new rating value.
        """
        reviews = self.reviews.all()
        if reviews.exists():
            avg_rating = reviews.aggregate(avg=Avg("rate"))["avg"]
            self.rating = round(avg_rating, 2)
        else:
            self.rating = 0.00
        self.save(update_fields=["rating"])
        return self.rating

    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['-created_at']


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/', blank=True, null=True, default='/products/placeholder.jpg')
    alt = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'


class Specification(models.Model):
    """
    Technical characteristics of a product.
    Linked to a specific Product instance.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'


class Review(models.Model):
    """
    Customer feedback and rating for a specific product.
    Includes unique constraint to prevent duplicate reviews by the same email per product.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    author_name = models.CharField(max_length=255, blank=True)
    text = models.TextField()
    email = models.EmailField()
    rate = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']
        unique_together = ['product', 'email']


class Sale(models.Model):
    """
    Promotional pricing with a specific validity period for a product.
    """
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='sale')
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_from = models.DateField()
    date_to = models.DateField()

    @property
    def is_active(self):
        """Check if the sale is currently valid based on today's date."""
        from django.utils import timezone
        return self.date_from <= timezone.now().date() <= self.date_to

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'


@receiver([post_save, post_delete], sender=Review)
def update_product_rating(sender, instance, **kwargs):
    """
    Automatically recalculates the product rating when saving or deleting a review.
    """
    if instance.product:
        instance.product.update_rating()
