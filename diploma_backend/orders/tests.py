from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from catalog.models import Category, Product
from orders.models import DeliverySettings, OrderItem, Order

User = get_user_model()


class OrderUnitTest(TestCase):
    """
    Unit tests for internal order logic.
    """

    def setUp(self):
        self.category = Category.objects.create(title="Food")
        self.product = Product.objects.create(title="Milk", price=Decimal("100.00"), category=self.category)

    def test_delivery_settings_singleton(self):
        """Ensure DeliverySettings always maintains a single record in the database."""
        s1 = DeliverySettings.load()
        s2 = DeliverySettings.load()
        self.assertEqual(s1.pk, s2.pk)
        self.assertEqual(DeliverySettings.objects.count(), 1)

    def test_order_item_total_price(self):
        """Verify the calculation of a single line item's price (quantity * price)."""
        order = Order.objects.create(total_cost=0)
        order_item = OrderItem.objects.create(product=self.product, order=order, quantity=2, price=self.product.price)

        order.total_cost = order_item.price * order_item.quantity
        order.save()

        self.assertEqual(order_item.total_price, self.product.price * 2)
        self.assertEqual(order.total_cost, self.product.price * 2)
        self.assertEqual(order_item.total_price, order.total_cost)

    def test_order_number_generation(self):
        """Ensure each created order receives a unique identification number."""
        order = Order.objects.create(total_cost=0)
        is_unique = Order.objects.filter(order_number=order.order_number)

        self.assertEqual(len(is_unique), 1)


class OrderApiTest(APITestCase):
    """
    API tests for order management and delivery calculation.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="test", password="pass", email="test@example.com")
        self.client.force_authenticate(user=self.user)
        self.order = Order.objects.create(user=self.user, total_cost=0, full_name=f"{self.user.username}",
                                          email=self.user.email)
        self.category = Category.objects.create(title="Tech")
        self.p1 = Product.objects.create(title="SSD", price=Decimal("1500.00"), category=self.category)

        self.delivery_cfg = DeliverySettings.load()
        self.delivery_cfg.free_delivery_threshold = Decimal("2000.00")
        self.delivery_cfg.standard_delivery_cost = Decimal("200.00")
        self.delivery_cfg.save()

    def test_create_order_from_items(self):
        """Verify that a POST request with product IDs correctly creates an Order and OrderItems."""
        url = reverse("orders:orders")
        response = self.client.post(url, data=[{"id": self.p1.id, "count": 2}], format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("orderId", response.data)

        order_id = response.data["orderId"]
        order = Order.objects.get(id=order_id)

        self.assertEqual(order.items.count(), 1)
        order_item = order.items.first()
        self.assertEqual(order_item.product, self.p1)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order.total_cost, Decimal("3000.00"))
        self.assertEqual(order_item.price, self.p1.price)

    def test_order_history_access(self):
        """Ensure users can only see their own orders and not orders from other sessions/users."""
        url = reverse("orders:orders")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        for i, _ in enumerate(response):
            self.assertEqual(self.user.email, response.data[i]["email"])
            self.assertEqual(self.user.username, response.data[i]["fullName"])

    def test_delivery_costs_logic(self):
        """Validate delivery cost calculation based on threshold and delivery type."""
        delivery_cfg = DeliverySettings.load()
        delivery_cfg.free_delivery_threshold = Decimal("2000.00")
        delivery_cfg.standard_delivery_cost = Decimal("200.00")
        delivery_cfg.express_delivery_surcharge = Decimal("500.00")
        delivery_cfg.save()

        url = reverse("orders:order_by_id", kwargs={"id": self.order.id})
        self.client.force_authenticate(user=self.user)

        data_cheap = {
            "fullName": "Annoying Orange",
            "email": "orange@mail.ru",
            "deliveryType": "regular",
            "totalCost": 1500.00,
            "city": "Moscow",
            "address": "Red Square 1",
            "phone": "88002000600",
            "status": "accepted",
            "paymentType": "online",
        }

        response = self.client.post(url, data_cheap, format="json")
        self.assertEqual(Decimal(str(response.data["totalCost"])), Decimal("1700.00"))

        data_expensive = data_cheap.copy()
        data_expensive["totalCost"] = 2500.00

        response = self.client.post(url, data_expensive, format="json")
        self.assertEqual(Decimal(str(response.data["totalCost"])), Decimal("2500.00"))

        data_express = data_cheap.copy()
        data_express["deliveryType"] = "express"
        data_express["totalCost"] = 3000.00

        response = self.client.post(url, data_express, format="json")
        self.assertEqual(Decimal(str(response.data["totalCost"])), Decimal("3500.00"))

    def test_finalize_order_details(self):
        """Check that updating address and contact info via POST on a specific order works correctly."""
        url = reverse("orders:order_by_id", kwargs={"id": self.order.id})
        self.client.force_authenticate(user=self.user)
        new_data = {
            "fullName": "Ivan Ivanov",
            "email": "ivan@example.com",
            "phone": "89001112233",
            "deliveryType": "regular",
            "paymentType": "online",
            "totalCost": 1000.00,
            "city": "Saint-Petersburg",
            "address": "Nevsky Prospect 1",
            "status": "accepted"
        }

        response = self.client.post(url, new_data, format="json")

        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual("Ivan Ivanov", self.order.full_name)
        self.assertEqual("ivan@example.com", self.order.email)
        self.assertEqual("89001112233", self.order.phone)
        self.assertEqual("Saint-Petersburg", self.order.city)
        self.assertEqual("Nevsky Prospect 1", self.order.address)
        self.assertEqual(response.data["fullName"], "Ivan Ivanov")
        self.assertEqual(response.data["address"], "Nevsky Prospect 1")
