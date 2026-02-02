from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from orders.models import Order
from .models import Payment
from .serializers import PaymentSerializer


@api_view(["POST"])
def payment_view(request, id):
    """
    Processes standard card payment for a specific order.
    Validates card details and updates order status upon success.
    """
    order = get_object_or_404(Order, id=id, user=request.user)

    serializer = PaymentSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    payment = serializer.save(order=order, amount=order.total_cost, payment_method='card')

    if payment.process_payment():
        return Response({"status": "success"}, status=status.HTTP_200_OK)

    return Response({"error": payment.error_message}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def payment_someone_view(request, id):
    """
    Processes payment using a random 'someone else's' account.
    Generates a valid random account number and completes the transaction.
    """
    order = get_object_or_404(Order, id=id, user=request.user)

    payment = Payment(
        order=order,
        payment_method='random_account',
        amount=order.total_cost
    )
    payment.card_number = payment.generate_random_account()
    payment.card_name = "Someone Else"
    payment.card_month = "12"
    payment.card_year = "2030"
    payment.card_code = "999"

    if payment.process_payment():
        return Response({"status": "success"}, status=status.HTTP_200_OK)

    return Response({"error": payment.error_message}, status=status.HTTP_400_BAD_REQUEST)
