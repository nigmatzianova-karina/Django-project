from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from cart.models import Cart, CartItem
from catalog.models import Product, Category

User = get_user_model()


class CartUnitTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password")
        self.category = Category.objects.create(title="Electronics")
        self.product = Product.objects.create(title="Laptop", price=100.00, category=self.category)
        self.cart = Cart.objects.create(user=self.user)

    def test_cart_total_calculations(self):
        """Checking the correctness of the cart total calculation"""
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

        self.assertEqual(self.cart.total_quantity, 2)
        self.assertEqual(self.cart.total_price, 200.00)


class CartApiTest(APITestCase):
    def setUp(self):
        self.url = reverse('cart:basket')
        self.category = Category.objects.create(title="Electronics")
        self.product = Product.objects.create(title="Laptop", price=100.00, category=self.category)
        self.user = User.objects.create_user(username="test", password="pass")
        self.client.force_authenticate(user=self.user)

    def test_add_item_to_cart(self):
        """Checking whether items have been added to the cart correctly via the endpoint"""
        data = {"id": self.product.id, "count": 3}
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data[0]['count'], 3)
        self.assertEqual(CartItem.objects.count(), 1)

    def test_delete_item_from_cart(self):
        """Checking whether items are removed from the cart correctly via the endpoint"""
        self.client.post(self.url, {"id": self.product.id, "count": 3}, format='json')
        response = self.client.delete(self.url, {"id": self.product.id, "count": 1}, format="json")

        self.assertEqual(response.status_code, 200)
        item = CartItem.objects.get(product=self.product)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(response.data[0]['count'], 2)

    def test_full_remove_item(self):
        """Verify that an item is completely removed when delete count >= current quantity."""
        self.client.post(self.url, {"id": self.product.id, "count": 1}, format='json')
        response = self.client.delete(self.url, {"id": self.product.id, "count": 1}, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 0)
        self.assertEqual(CartItem.objects.count(), 0)
