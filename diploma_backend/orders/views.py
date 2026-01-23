from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import random

from cart.models import CartItem
from catalog.models import Product
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer


@api_view(["GET", "POST"])
def orders_view(request):
    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    if request.method == "GET":
        if request.user.is_authenticated:
            orders = Order.objects.filter(
                user=request.user,
            ).order_by("-created_at")
        else:
            orders = Order.objects.filter(
                session_id=session_id,
            ).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    elif request.method == "POST":
        order_number = random.randint(111111111, 999999999)
        total_cost = 0
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            session_id=session_id if not request.user.is_authenticated else None,
            total_cost=total_cost,
            order_number=order_number,
        )

        for item in request.data:
            product = Product.objects.get(
                id=item["id"]
            )
            cart_item = CartItem.objects.filter(
                product=product,
            ).first()
            order_item = OrderItem.objects.create(
                order=order,
                product=product,
                quantity=cart_item.quantity,
                price=cart_item.total_price
            )
            order_item.save()
            total_cost += order_item.price

        order.total_cost = total_cost

        order.save()
        return Response({"orderId": int(order.id)})

    return Response(status=400)


@api_view(["GET", "POST"])
def orders_by_id_view(request, id):
    print("start")

    if not request.session.session_key:
        request.session.create()

    session_id = request.session.session_key

    if request.method == "GET":
        if request.user.is_authenticated:
            order = Order.objects.get(
                user=request.user,
                id=id
            )
        else:
            order = Order.objects.get(
                session_id=session_id,
                id=id
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data)
    elif request.method == "POST":
        order = Order.objects.get(
            user=request.user,
            id=id
        )
        order.full_name = request.data.get("fullName")
        order.email = request.data.get("email")
        order.phone = request.data.get("phone")
        order.delivery_type = request.data.get("deliveryType")
        order.payment_type = request.data.get("paymentType")
        order.total_cost = request.data.get("totalCost")
        order.status = request.data.get("status")
        order.city = request.data.get("city")
        order.address = request.data.get("address")

        print(order.delivery_type)

        if order.delivery_type == "express":
            print("express")
            order.delivery_cost = 500
            order.total_cost = float(order.total_cost) + order.delivery_cost
        elif order.delivery_type == "ordinary" and float(order.total_cost) < 2000:
            print("ordinary < 2000")
            order.delivery_cost = 200
            order.total_cost = float(order.total_cost) + order.delivery_cost
        else:
            print("ordinary > 2000")
            order.delivery_cost = 0

        order.save()

        products = OrderItem.objects.filter(order=order)
        for product in products:
            print(product)
        serializer = OrderSerializer(order)
        data = serializer.data
        data["orderId"] = order.id
        print(data)
        return Response(data, status=200)

    return Response(status=400)
