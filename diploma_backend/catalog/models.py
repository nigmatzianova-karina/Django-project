from django.conf import settings
from django.db import models
from django.db.models import Avg


class Category(models.Model):
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='', blank=True, null=True, default='/static/categories/placeholder.jpg')
    is_active = models.BooleanField(default=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_featured = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['title']


class Tag(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    full_description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    count = models.PositiveIntegerField(default=0)
    limited_edition = models.BooleanField(default=False)
    free_delivery = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    rating = models.FloatField(default=0.0)

    sort_index = models.IntegerField(default=0)
    purchases_count = models.PositiveIntegerField(default=0)

    is_banner = models.BooleanField(default=False)
    banner_order = models.IntegerField(default=0)
    banner_text = models.TextField(blank=True)

    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    tags = models.ManyToManyField(Tag, blank=True)

    @property
    def reviews_count(self):
        return self.reviews.count()

    @property
    def date(self):
        """Возвращает дату в формате как в API"""
        return self.created_at.strftime('%a %b %d %Y %H:%M:%S GMT%z')

    def update_rating(self):
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
    image = models.ImageField(upload_to='', default='/static/products/placeholder.jpg')
    alt = models.CharField(max_length=255, blank=True)
    is_main = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'


class Specification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    name = models.CharField(max_length=255)
    value = models.CharField(max_length=255)

    class Meta:
        verbose_name = 'Характеристика'
        verbose_name_plural = 'Характеристики'


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='reviews',
                               null=True, blank=True)

    author_name = models.CharField(max_length=255)
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
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='sale')
    sale_price = models.DecimalField(max_digits=10, decimal_places=2)
    date_from = models.DateField()
    date_to = models.DateField()

    @property
    def dateFrom(self):
        return self.date_from.strftime('%m-%d')

    @property
    def dateTo(self):
        return self.date_to.strftime('%m-%d')

    class Meta:
        verbose_name = 'Скидка'
        verbose_name_plural = 'Скидки'
