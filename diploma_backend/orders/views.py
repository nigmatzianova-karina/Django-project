from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
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
        pass
    return Response(status=400)


@api_view(["GET", "POST"])
def orders_by_id_view(request, id):
    if request.method == "GET":
        order = Order.objects.filter(
            user=request.user,
            id=id
        )
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    elif request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            full_name=request.data.get("fullName"),
            email=request.data.get("email"),
            phone=request.data.get("phone"),
            delivery_type=request.data.get("deliveryType"),
            payment_type=request.data.gat("paymentType"),
            total_cost=request.data.get("totalCost"),
            status=request.data.get("status"),
            city=request.data.get("city"),
            address=request.data.get("address")
        )

        products = request.data.get("products", [])
        if products:
            for product in products:
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=product.count,
                    price=product.price
                )

        return Response(status=200)
    return Response(status=400)