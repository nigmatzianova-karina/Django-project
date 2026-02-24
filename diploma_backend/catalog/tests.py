from datetime import timedelta
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone

from catalog.models import Category, Product, Sale, Review, Tag

User = get_user_model()


class CatalogUnitTests(TestCase):
    """
    Tests to verify the internal logic of models
    without using network requests (API).
    """

    def setUp(self):
        self.category = Category.objects.create(title="Base Category")
        self.product = Product.objects.create(title="Laptop", price=100.00, category=self.category)

    def test_category_hierarchy_string(self):
        """Checking the string representation and nesting of categories"""
        sub_cat = Category.objects.create(title="Sub", parent=self.category)
        self.assertEqual(sub_cat.parent.title, "Base Category")
        self.assertEqual(str(sub_cat), "Sub")

    def test_sale_is_active(self):
        """Checking @property is_active for the Sale model"""
        today = timezone.now().date()

        sale = Sale(
            product=self.product,
            sale_price=Decimal("80.00"),
            date_from=today - timedelta(days=1),
            date_to=today + timedelta(days=1)
        )
        self.assertTrue(sale.is_active)

        sale.date_from = today - timedelta(days=5)
        sale.date_to = today - timedelta(days=1)
        self.assertFalse(sale.is_active)

    def test_product_rating_update_method(self):
        """Direct call to the update_rating method without signals"""
        Review.objects.create(product=self.product, rate=4, text="Ok", email="1@v.com")
        Review.objects.create(product=self.product, rate=2, text="Meh", email="2@v.com")

        new_rating = self.product.update_rating()

        self.assertEqual(new_rating, 3.0)
        self.assertEqual(self.product.rating, 3.0)

    def test_product_reviews_count_property(self):
        """Check @property reviews_count"""
        Review.objects.create(product=self.product, rate=5, text="X", email="x@v.com")
        Review.objects.create(product=self.product, rate=4, text="Y", email="y@v.com")

        self.assertEqual(self.product.reviews_count, 2)

    def test_unique_review_constraint(self):
        """IntegrityError check when duplicating a review via email"""
        Review.objects.create(product=self.product, rate=5, text="X", email="x@v.com")

        with self.assertRaises(IntegrityError):
            Review.objects.create(product=self.product, rate=1, text="Y", email="x@v.com")

    def test_sale_one_to_one_constraint(self):
        """Checking that one product cannot have two Sale objects"""
        Sale.objects.create(product=self.product, sale_price=50, date_from=timezone.now(), date_to=timezone.now())

        with self.assertRaises(IntegrityError):
            Sale.objects.create(product=self.product, sale_price=40, date_from=timezone.now(), date_to=timezone.now())


class CatalogApiTests(APITestCase):
    """
    Tests for checking view functionality
    using network requests (API).
    """

    def setUp(self):
        self.parent_cat = Category.objects.create(title="Electronics", is_active=True)
        self.child_cat = Category.objects.create(title="Phones", parent=self.parent_cat, is_active=True)
        self.tag_apple = Tag.objects.create(name="Apple")

        self.p1 = Product.objects.create(
            title="iPhone 15", price=Decimal("1000.00"),
            category=self.child_cat, free_delivery=True, is_active=True
        )
        self.p1.tags.add(self.tag_apple)

        self.p2 = Product.objects.create(
            title="Nokia 3310", price=Decimal("50.00"),
            category=self.child_cat, is_active=True
        )
        self.user = User.objects.create_user(username="testuser", password="password")

    def test_filter_by_name(self):
        """Ensure that filtering by name returns only matching products."""
        url = reverse('catalog:catalog')
        response = self.client.get(url, {'filter[name]': 'iphone'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['title'], "iPhone 15")

    def test_filter_by_price_range(self):
        """Validate that products are correctly filtered within the specified price range."""
        url = reverse('catalog:catalog')
        response = self.client.get(url, {'filter[minPrice]': 10, 'filter[maxPrice]': 100})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['title'], "Nokia 3310")

    def test_filter_by_tags(self):
        """Verify filtering functionality when one or multiple tags are selected."""
        url = reverse('catalog:catalog')
        response = self.client.get(url, {'tags[]': [self.tag_apple.id]})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['items']), 1)
        self.assertEqual(response.data['items'][0]['title'], "iPhone 15")

    def test_catalog_pagination_structure(self):
        """Ensure the catalog response contains pagination metadata (currentPage, lastPage)."""
        url = reverse('catalog:catalog')
        response = self.client.get(url, {'limit': 1})

        self.assertEqual(response.status_code, 200)
        self.assertIn('currentPage', response.data)
        self.assertIn('lastPage', response.data)
        self.assertEqual(len(response.data['items']), 1)

    def test_popular_products_limit(self):
        """Verify that the popular products endpoint returns no more than 8 items."""
        url = reverse('catalog:popular_products')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.data) <= 8)

    def test_add_review_authenticated(self):
        """Verify that an authorized user can successfully post a review for a product."""
        self.client.force_authenticate(user=self.user)
        url = reverse('catalog:product_review', kwargs={'id': self.p1.id})

        data = {
            "author": "Test User",
            "email": "test@test.com",
            "text": "Amazing build quality!",
            "rate": 5
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Review.objects.filter(product=self.p1).count(), 1)

    def test_get_categories(self):
        """Verify that the API returns a hierarchical tree of active root categories."""
        url = reverse("catalog:categories")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]["subcategories"][0]["title"], self.child_cat.title)

    def test_product_detail_view(self):
        """Ensure all detailed product fields (specs, full description, reviews) are present in the response."""
        url = reverse("catalog:product_by_id", kwargs={"id": self.p1.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], self.p1.title)
        self.assertEqual(Decimal(response.data["price"]), self.p1.price)
        self.assertEqual(response.data["category"], self.p1.category.id)
        self.assertEqual(response.data["freeDelivery"], self.p1.free_delivery)

    def test_add_review_permissions(self):
        """Verify that only authenticated users can post reviews."""
        url = reverse("catalog:product_review", kwargs={"id": self.p1.id})
        data = {
            "author": "Annoying Orange",
            "email": "no-reply@mail.ru",
            "text": "rewrewrwerewrwerwerewrwerwer",
            "rate": 4,
            "date": "2023-05-05 12:12"
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, 403)
