from django.conf import settings
from django.db import models

from catalog.models import Product


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('accepted', 'Принят'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]
    PAYMENT_TYPES = [
        ("online", "Онлайн картой"),
        ("random_account", "Онлайн со случайного чужого счёта"),
    ]
    DELIVERY_TYPES = [
        ("express", "Экспресс доставка"),
        ("free", "Бесплатная доставка"),
        ("regular", "Обычная доставка"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name="orders", null=True,
                             blank=True, verbose_name="Пользователь")
    session_id = models.CharField(max_length=255, null=True, blank=True)
    order_number = models.CharField(max_length=20, unique=True, verbose_name='Номер заказа')
    full_name = models.CharField(max_length=255, verbose_name="ФИО")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")

    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPES, verbose_name="Тип доставки")
    city = models.CharField(max_length=55, verbose_name="Город доставки")
    address = models.CharField(max_length=255, verbose_name="Адрес доставки")
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Стоимость доставки")
    comment = models.TextField(blank=True, verbose_name="Комментарий к заказу")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус заказа')

    payment_type = models.CharField(max_length=35, choices=PAYMENT_TYPES, verbose_name="Способ оплаты")
    payment_status = models.CharField(max_length=50, blank=True, verbose_name='Статус оплаты')
    payment_error = models.TextField(blank=True, verbose_name='Текст ошибки оплаты')
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Общая стоимость")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата удаления')

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='Заказ')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='Товар')
    quantity = models.PositiveIntegerField(verbose_name='Количество')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена на момент покупки')

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'


class DeliverySettings(models.Model):
    free_delivery_threshold = models.DecimalField(
        max_digits=10, decimal_places=2, default=2000.00,
        verbose_name='Порог бесплатной доставки (руб)',
        help_text='Заказ от этой суммы получает бесплатную доставку'
    )

    standard_delivery_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=200.00,
        verbose_name='Стоимость обычной доставки (руб)',
        help_text='Цена доставки для заказов ниже порога'
    )

    express_delivery_surcharge = models.DecimalField(
        max_digits=10, decimal_places=2, default=500.00,
        verbose_name='Надбавка за экспресс-доставку (руб)',
        help_text='Дополнительная плата за срочную доставку'
    )

    class Meta:
        verbose_name = 'Настройки доставки'
        verbose_name_plural = 'Настройки доставки'

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "Настройки доставки"

    @classmethod
    def load(cls):
        """Получить настройки (создать если нет)"""
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
