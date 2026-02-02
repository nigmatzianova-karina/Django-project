from decimal import Decimal

from django.db import transaction
from rest_framework.decorators import api_view
from rest_framework.response import Response
import random
from catalog.models import Product
from orders.models import Order, OrderItem, DeliverySettings
from orders.serializers import OrderSerializer


@api_view(["GET", "POST"])
def orders_view(request):
    """
    Handles order history retrieval and initial order creation from cart items.
    Generates a unique order number and calculates preliminary totals.
    """
    session_id = request.session.session_key or request.session.create()

    if request.method == "GET":
        orders = Order.objects.filter(
            user=request.user if request.user.is_authenticated else None,
            session_id=None if request.user.is_authenticated else session_id
        ).prefetch_related(
            'items__product__images', 'items__product__tags'
        ).order_by("-created_at")

        return Response(OrderSerializer(orders, many=True).data)

    elif request.method == "POST":
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_id=session_id if not request.user.is_authenticated else None,
                total_cost=0,
                order_number=random.randint(100000, 999999),
            )

            total_cost = 0
            for item_data in request.data:
                product = Product.objects.get(id=item_data["id"])

                order_item = OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item_data.get("count", 1),
                    price=product.price
                )
                total_cost += order_item.price * order_item.quantity

            order.total_cost = total_cost
            order.save()

        return Response({"orderId": order.id})

    return Response(status=400)


@api_view(["GET", "POST"])
def orders_by_id_view(request, id):
    """
    Manages detailed order information.
    GET: Returns full order details including nested products.
    POST: Finalizes order details (address, delivery) and applies delivery costs.
    """
    delivery_cfg = DeliverySettings.load()

    try:
        if request.user.is_authenticated:
            order = Order.objects.get(user=request.user, id=id)
        else:
            order = Order.objects.get(session_id=request.session.session_key, id=id)
    except Order.DoesNotExist:
        return Response(status=404)

    if request.method == "GET":
        return Response(OrderSerializer(order).data)

    elif request.method == "POST":
        order.full_name = request.data.get("fullName", order.full_name)
        order.email = request.data.get("email")
        order.phone = request.data.get("phone")
        order.delivery_type = request.data.get("deliveryType")
        order.payment_type = request.data.get("paymentType")
        order.total_cost = request.data.get("totalCost")
        order.status = request.data.get("status")
        order.city = request.data.get("city")
        order.address = request.data.get("address")

        delivery_cfg = DeliverySettings.load()

        current_total = Decimal(str(request.data.get("totalCost", order.total_cost)))

        if order.delivery_type == "express":
            order.delivery_cost = delivery_cfg.express_delivery_surcharge
        elif current_total < delivery_cfg.free_delivery_threshold:
            order.delivery_cost = delivery_cfg.standard_delivery_cost
        else:
            order.delivery_cost = Decimal("0.00")

        order.total_cost = current_total + order.delivery_cost
        order.save()

        serializer = OrderSerializer(order)
        data = serializer.data
        data["orderId"] = order.id
        return Response(data)

    return Response(status=400)
