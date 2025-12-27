from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import random
from catalog.models import Product
from orders.models import Order, OrderItem
from orders.serializers import OrderSerializer


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def orders_view(request):
    if request.method == "GET":
        orders = Order.objects.filter(
            user=request.user,
        ).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        order_number = random.randint(111111111, 999999999)
        order = Order.objects.create(
            user=request.user,
            total_cost=0,
            order_number=order_number,
        )
        for item in request.data:
            product = Product.objects.get(
                id=item["id"]
            )
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=item["count"],
                price=item["price"]
            )
        return Response({"orderId": int(order.id)})

    return Response(status=400)


@api_view(["GET", "POST"])
def orders_by_id_view(request, id):
    print("start")
    if request.method == "GET":
        order = Order.objects.get(
            user=request.user,
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

        products = request.data.get("products", [])
        for product in products:
            item, _ = OrderItem.objects.get_or_create(
                order=order,
                product=product,
                quantity=product.count,
                price=product.price
            )
        return Response(status=200)
    return Response(status=400)
