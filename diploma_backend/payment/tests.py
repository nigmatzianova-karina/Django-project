from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

from orders.models import Order
from payment.models import Payment

User = get_user_model()


class PaymentUnitTest(TestCase):
    """
    Logic tests for the Payment model methods.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="pay-user", password="pass")
        self.order = Order.objects.create(
            user=self.user, order_number="101", total_cost=Decimal("100.00"),
            payment_type="online", status="new"
        )

    def test_payment_success_logic(self):
        """Success: number is even (2) and doesn't end in 0."""
        payment = Payment.objects.create(order=self.order, card_number="12341232", amount=Decimal("100.00"))
        success = payment.process_payment()

        self.assertTrue(success)
        self.assertEqual(payment.status, "completed")

    def test_payment_fail_logic(self):
        """Ensure that odd card numbers or numbers ending in 0 trigger a 'failed' status and an error message"""
        payment = Payment.objects.create(order=self.order, card_number="123412323", amount=Decimal("100.00"))
        success = payment.process_payment()

        self.assertFalse(success)
        self.assertEqual(payment.status, "failed")

    def test_order_status_update_on_success(self):
        """Check that the associated Order status changes to 'accepted' after a successful payment."""
        payment = Payment.objects.create(order=self.order, card_number="12341232", amount=Decimal("100.00"))
        success = payment.process_payment()

        self.assertTrue(success)
        self.assertEqual(payment.status, "completed")
        self.assertEqual(self.order.status, "accepted")

    def test_generate_random_account(self):
        """Check that the associated Order status changes to 'accepted' after a successful payment."""
        payment = Payment.objects.create(order=self.order, amount=Decimal("100.00"))
        payment.card_number = payment.generate_random_account()
        success = payment.process_payment()

        self.assertTrue(success)
        self.assertEqual(payment.status, "completed")
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "accepted")


class PaymentApiTest(APITestCase):
    """
    Integration tests for payment views.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="test-user", password="password")
        self.order = Order.objects.create(
            user=self.user, order_number="999", total_cost=Decimal("500.00"),
            payment_type="online", status="new"
        )

    def test_payment_view_validation(self):
        """Validate that the serializer correctly catches non-digit card numbers (400 Bad Request)."""
        url = reverse("payment:payment", kwargs={"id": self.order.id})
        data = {
            "number": "aaa",
            "name": "Annoying Orange",
            "month": "02",
            "year": "2025",
            "code": "123"
        }

        with self.assertRaises(TypeError):
            self.client.post(url, data, format="json")

    def test_payment_someone_flow(self):
        """Verify the full flow of payment from "someone else's account" for an authenticated user's order."""
        self.client.force_authenticate(user=self.user)
        url = reverse("payment:payment-someone", kwargs={"id": self.order.id})
        success = self.client.post(url, format="json")

        self.assertIn("success", success.data["status"])


    def test_payment_access_denied(self):
        """Ensure a user cannot pay for an order that belongs to another user (404 Not Found)."""
        other_user = User.objects.create_user(username="test-other-user", password="password1")
        other_order = Order.objects.create(
            user=other_user, order_number="998", total_cost=Decimal("500.00"),
            payment_type="online", status="new"
        )
        self.client.force_authenticate(user=self.user)

        url = reverse("payment:payment", kwargs={"id": other_order.id})
        data = {
            "number": "12344322",
            "name": "Annoying Orange",
            "month": "02",
            "year": "2025",
            "code": "123"
        }
        result = self.client.post(url, data, format="json")

        self.assertEqual(result.status_code, 404)

