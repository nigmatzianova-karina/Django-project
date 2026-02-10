import random

from django.db import models
from django.db.models import CASCADE

from orders.models import Order


class Payment(models.Model):
    """
    Stores payment transaction details and validates them against business rules.

    Business Logic:
    - Payment is successful if the card number is even and does not end in 0.
    - Otherwise, a random bank error is generated.
    """
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

    card_number = models.CharField(max_length=16, verbose_name="Номер карты/счета")
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
        """
        Executes the payment validation logic.
        Updates the payment status and records error messages if the transaction fails.
        Returns:
            bool: True if payment was successful, False otherwise.
        """
        clean_number = ''.join(filter(str.isdigit, self.card_number))

        try:
            num_val = int(clean_number)
            last_digit = num_val % 10
            is_even = num_val % 2 == 0

            success = is_even and last_digit != 0
        except ValueError:
            success = False

        if success:
            self.status = 'completed'
            self.error_message = ""
            self.order.status = "accepted"
            self.order.save()
        else:
            self.status = 'failed'
            self.error_message = random.choice([
                "Недостаточно средств",
                "Карта отклонена банком",
                "Срок действия карты истек",
                "Неверный CVV код",
                "Превышен лимит операций"
            ])

        self.save()
        return success

    def generate_random_account(self):
        """
        Utility method to generate a 8-digit account number according to the requirements.
        The resulting number always ends with an even digit to satisfy success conditions.
        """
        import random
        return str(random.randint(1000000, 9999999)) + str(random.choice([2, 4, 6, 8]))
