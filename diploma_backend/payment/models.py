from django.db import models
from django.db.models import CASCADE

from orders.models import Order


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает оплаты'),
        ('processing', 'В обработке'),
        ('completed', 'Оплачено'),
        ('failed', 'Ошибка оплаты'),
        ('refunded', 'Возвращено'),
    ]

    PAYMENT_METHODS = [
        ('card', 'Онлайн картой'),
        ('random_account', 'Онлайн со случайного чужого счёта'),
    ]

    order = models.ForeignKey(Order, on_delete=CASCADE, related_name="payment", verbose_name="Заказ")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name="Способ оплаты")

    card_number = models.CharField(max_length=8, verbose_name="Номер карты/счета")
    card_name = models.CharField(max_length=255, verbose_name="Имя на карте")
    card_month = models.CharField(max_length=2, verbose_name="Месяц окончания")
    card_year = models.CharField(max_length=4, verbose_name="Год окончания")
    card_code = models.CharField(max_length=4, verbose_name="CVV/CVC код")

    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Статус")

    error_message = models.TextField(blank=True, verbose_name="Сообщение об ошибке")
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID транзакции")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Платеж'
        verbose_name_plural = 'Платежи'
        ordering = ['-created_at']

    def __str__(self):
        return f"Платеж #{self.id} для заказа {self.order.order_number}"

    def process_payment(self):
        """Обработка платежа по логике ТЗ"""
        clean_number = ''.join(filter(str.isdigit, self.card_number))

        last_digit = int(clean_number[-1]) if clean_number else 0
        is_even = int(clean_number) % 2 == 0 if clean_number else False

        if is_even and last_digit != 0:
            self.status = 'completed'
            self.error_message = ''
        else:
            self.status = 'failed'
            import random
            errors = [
                "Недостаточно средств",
                "Карта отклонена банком",
                "Срок действия карты истек",
                "Неверный CVV код",
                "Превышен лимит операций"
            ]
            self.error_message = random.choice(errors)

        self.save()
        return self.status == 'completed'

    def generate_random_account(self):
        """Генерация случайного счета по ТЗ"""
        import random
        return str(random.randint(1000000, 9999999)) + str(random.choice([2, 4, 6, 8]))
