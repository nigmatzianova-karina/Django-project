from rest_framework.decorators import api_view
from rest_framework.response import Response

from orders.models import Order
from .models import Payment


@api_view(["POST"])
def payment_view(request):
    order = Order.objects.get(
        user=request.user,
    )
    payment = Payment(
        order=order,
        card_number=request.data.get("number"),
        card_name=request.data.get("name"),
        card_month=request.data.get("mouth"),
        card_year=request.data.get("year"),
        card_code=request.data.get("code")
    )

    return Response(status=200)
