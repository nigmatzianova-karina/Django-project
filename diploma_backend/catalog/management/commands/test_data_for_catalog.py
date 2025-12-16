# catalog/management/commands/seed_catalog.py
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from catalog.models import Category, Product, Review, Sale, Specification, Tag

User = get_user_model()


class Command(BaseCommand):
    help = 'Заполняет базу тестовыми данными для каталога'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Удалить существующие данные перед созданием новых'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.clear_data()

        self.create_categories()
        self.create_tags()
        self.create_products()
        self.create_reviews()
        self.create_sales()
        self.create_specifications()

        self.stdout.write(self.style.SUCCESS('✅ Тестовые данные успешно созданы!'))

    def clear_data(self):
        """Удалить все существующие данные"""
        self.stdout.write('🗑️  Удаление существующих данных...')
        Review.objects.all().delete()
        Specification.objects.all().delete()
        Sale.objects.all().delete()
        Product.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        self.stdout.write('   Данные удалены.')

    def create_categories(self):
        """Создать категории"""
        self.stdout.write('📂 Создание категорий...')

        # Родительские категории
        electronics = Category.objects.create(
            title='Электроника',
            is_active=True,
            is_featured=True
        )

        clothes = Category.objects.create(
            title='Одежда',
            is_active=True,
            is_featured=False
        )

        books = Category.objects.create(
            title='Книги',
            is_active=True,
            is_featured=True
        )

        # Подкатегории для электроники
        Category.objects.create(
            title='Смартфоны',
            parent=electronics,
            is_active=True,
            is_featured=True
        )

        Category.objects.create(
            title='Ноутбуки',
            parent=electronics,
            is_active=True,
            is_featured=False
        )

        Category.objects.create(
            title='Наушники',
            parent=electronics,
            is_active=True,
            is_featured=True
        )

        # Подкатегории для одежды
        Category.objects.create(
            title='Мужская одежда',
            parent=clothes,
            is_active=True
        )

        Category.objects.create(
            title='Женская одежда',
            parent=clothes,
            is_active=True
        )

        self.stdout.write(f'   Создано {Category.objects.count()} категорий.')

    def create_tags(self):
        """Создать теги"""
        self.stdout.write('🏷️  Создание тегов...')

        tags = [
            'Apple', 'Android', 'Флагман', 'Бюджетный',
            'Новинка', 'Хит продаж', 'Со скидкой',
            'Игровой', 'Для работы', 'Премиум'
        ]

        for tag_name in tags:
            Tag.objects.get_or_create(name=tag_name)

        self.stdout.write(f'   Создано {Tag.objects.count()} тегов.')

    def create_products(self):
        """Создать товары"""
        self.stdout.write('📱 Создание товаров...')

        # Получаем категории
        smartphones = Category.objects.get(title='Смартфоны')
        laptops = Category.objects.get(title='Ноутбуки')
        headphones = Category.objects.get(title='Наушники')

        # Получаем теги
        tag_apple = Tag.objects.get(name='Apple')
        tag_android = Tag.objects.get(name='Android')
        tag_flagship = Tag.objects.get(name='Флагман')
        tag_new = Tag.objects.get(name='Новинка')
        tag_premium = Tag.objects.get(name='Премиум')
        tag_gaming = Tag.objects.get(name='Игровой')

        # Список товаров для создания
        products_data = [
            {
                'title': 'iPhone 15 Pro',
                'description': 'Флагманский смартфон Apple с процессором A17 Pro, камерой 48 МП и дисплеем Super Retina XDR.',
                'price': Decimal('99999.00'),
                'category': smartphones,
                'is_active': True,
                'rating': 4.8,
                'free_delivery': True,
                'tags': [tag_apple, tag_flagship, tag_new, tag_premium]
            },
            {
                'title': 'Samsung Galaxy S24',
                'description': 'Android-смартфон с камерой 200 МП, процессором Snapdragon 8 Gen 3 и аккумулятором 5000 мАч.',
                'price': Decimal('79999.00'),
                'category': smartphones,
                'is_active': True,
                'rating': 4.6,
                'free_delivery': True,
                'tags': [tag_android, tag_flagship, tag_new]
            },
            {
                'title': 'Xiaomi Redmi Note 13',
                'description': 'Бюджетный смартфон с хорошей камерой и автономностью.',
                'price': Decimal('24999.00'),
                'category': smartphones,
                'is_active': True,
                'rating': 4.2,
                'free_delivery': False,
                'tags': [tag_android]
            },
            {
                'title': 'MacBook Air M3',
                'description': 'Легкий и мощный ноутбук с процессором Apple M3, 16 ГБ памяти и дисплеем Liquid Retina.',
                'price': Decimal('129999.00'),
                'category': laptops,
                'is_active': True,
                'rating': 4.9,
                'free_delivery': True,
                'tags': [tag_apple, tag_premium]
            },
            {
                'title': 'ASUS ROG Zephyrus',
                'description': 'Игровой ноутбук с видеокартой RTX 4070 и процессором Intel Core i9.',
                'price': Decimal('189999.00'),
                'category': laptops,
                'is_active': True,
                'rating': 4.7,
                'free_delivery': True,
                'tags': [tag_gaming, tag_premium]
            },
            {
                'title': 'Apple AirPods Pro 2',
                'description': 'Беспроводные наушники с активным шумоподавлением и пространственным звуком.',
                'price': Decimal('24999.00'),
                'category': headphones,
                'is_active': True,
                'rating': 4.5,
                'free_delivery': True,
                'tags': [tag_apple, tag_new]
            },
            {
                'title': 'Sony WH-1000XM5',
                'description': 'Наушники с лучшим в классе шумоподавлением и звуком высокого разрешения.',
                'price': Decimal('34999.00'),
                'category': headphones,
                'is_active': True,
                'rating': 4.8,
                'free_delivery': True,
                'tags': [tag_premium]
            },
            {
                'title': 'Устаревшая модель (архив)',
                'description': 'Старый товар, снятый с продажи. Используется для тестирования фильтров.',
                'price': Decimal('15000.00'),
                'category': smartphones,
                'is_active': False,  # ⚠️ Не активен!
                'rating': 3.2,
                'free_delivery': False,
                'tags': []
            }
        ]

        # Создаем товары
        for product_data in products_data:
            tags = product_data.pop('tags', [])
            product = Product.objects.create(**product_data)
            if tags:
                product.tags.set(tags)

        self.stdout.write(f'   Создано {Product.objects.count()} товаров.')

    def create_reviews(self):
        """Создать отзывы"""
        self.stdout.write('⭐ Создание отзывов...')

        # Получаем пользователя (создадим тестового, если нет)
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com', 'is_active': True}
        )

        if created:
            user.set_password('123456')
            user.save()

        products = Product.objects.filter(is_active=True)
        reviews_created = 0

        # Список для генерации уникальных отзывов
        email_domains = ['gmail.com', 'yandex.ru', 'mail.ru', 'outlook.com']
        first_names = ['Алексей', 'Мария', 'Дмитрий', 'Анна', 'Иван', 'Елена', 'Сергей', 'Ольга']
        last_names = ['Иванов', 'Петрова', 'Сидоров', 'Кузнецова', 'Смирнов', 'Попова']

        for product in products:
            # Создаем 2-4 отзыва на каждый товар
            num_reviews = random.randint(2, 4)

            # Счетчик для уникальных email на этот товар
            emails_used = set()

            for i in range(num_reviews):
                # Генерируем УНИКАЛЬНЫЙ email для этого товара
                first_name = random.choice(first_names)
                last_name = random.choice(last_names)
                email = f"{first_name.lower()}.{last_name.lower()}{i + 1}{product.id}@{random.choice(email_domains)}"

                # Добавляем ID товара в email для гарантии уникальности
                if email in emails_used:
                    email = f"{first_name.lower()}.{last_name.lower()}{i + 1}{product.id}{random.randint(100, 999)}@{random.choice(email_domains)}"

                emails_used.add(email)

                rate = random.choice([4, 5]) if product.rating > 4 else random.choice([3, 4, 5])
                author_name = f"{first_name} {last_name}"

                Review.objects.create(
                    product=product,
                    author=user if random.choice([True, False]) else None,
                    author_name=author_name,
                    email=email,  # Уникальный email
                    text=random.choice([
                        f'Отличный товар! {product.title} полностью оправдал ожидания.',
                        f'Пользуюсь уже месяц, всё работает отлично.',
                        f'Хорошее качество за свои деньги.',
                        f'Недостатки: {random.choice(["тяжеловат", "быстро садится батарея", "дорогой"])}.',
                        f'Лучшая покупка за последнее время!'
                    ]),
                    rate=rate
                )
                reviews_created += 1

        self.stdout.write(f'   Создано {reviews_created} отзывов.')

    def create_sales(self):
        """Создать скидки"""
        self.stdout.write('🏷️  Создание скидок...')

        today = timezone.now().date()

        # Товары для скидок
        products_for_sale = Product.objects.filter(is_active=True)[:3]

        # Создаем скидки
        for i, product in enumerate(products_for_sale):
            if i == 0:
                # Активная скидка
                Sale.objects.create(
                    product=product,
                    sale_price=product.price * Decimal('0.8'),  # -20%
                    date_from=today,
                    date_to=today + timezone.timedelta(days=7)
                )
            elif i == 1:
                # Будущая скидка
                Sale.objects.create(
                    product=product,
                    sale_price=product.price * Decimal('0.85'),  # -15%
                    date_from=today + timezone.timedelta(days=3),
                    date_to=today + timezone.timedelta(days=10)
                )
            else:
                # Прошедшая скидка
                Sale.objects.create(
                    product=product,
                    sale_price=product.price * Decimal('0.7'),  # -30%
                    date_from=today - timezone.timedelta(days=10),
                    date_to=today - timezone.timedelta(days=1)
                )

        self.stdout.write(f'   Создано {Sale.objects.count()} скидок.')

    def create_specifications(self):
        """Создать характеристики для товаров"""
        self.stdout.write('📋 Создание характеристик...')

        products = Product.objects.filter(is_active=True)

        # Шаблоны характеристик по категориям
        specs_templates = {
            'Смартфоны': [
                ('Диагональ экрана', ['6.1"', '6.7"', '6.3"']),
                ('Память', ['128 ГБ', '256 ГБ', '512 ГБ']),
                ('Оперативная память', ['8 ГБ', '12 ГБ', '16 ГБ']),
                ('Цвет', ['Черный', 'Белый', 'Синий', 'Фиолетовый']),
                ('Батарея', ['4000 мАч', '4500 мАч', '5000 мАч'])
            ],
            'Ноутбуки': [
                ('Диагональ экрана', ['13"', '14"', '15.6"', '16"']),
                ('Процессор', ['Apple M3', 'Intel Core i7', 'AMD Ryzen 7']),
                ('Оперативная память', ['8 ГБ', '16 ГБ', '32 ГБ']),
                ('SSD', ['256 ГБ', '512 ГБ', '1 ТБ']),
                ('Видеокарта', ['Встроенная', 'RTX 4050', 'RTX 4070'])
            ],
            'Наушники': [
                ('Тип', ['Накладные', 'Вкладыши', 'Внутриканальные']),
                ('Шумоподавление', ['Активное', 'Пассивное', 'Нет']),
                ('Время работы', ['20 часов', '30 часов', '40 часов']),
                ('Водозащита', ['IPX4', 'IPX7', 'Нет']),
                ('Вес', ['250 г', '300 г', '350 г'])
            ]
        }

        specs_created = 0

        for product in products:
            category_name = product.category.title
            if category_name in specs_templates:
                for spec_name, possible_values in specs_templates[category_name]:
                    Specification.objects.create(
                        product=product,
                        name=spec_name,
                        value=random.choice(possible_values)
                    )
                    specs_created += 1

        self.stdout.write(f'   Создано {specs_created} характеристик.')
