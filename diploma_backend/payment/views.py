from rest_framework.decorators import api_view
from rest_framework.response import Response
from orders.models import Order
from .models import Payment


@api_view(["POST"])
def payment_view(request, id):
    print("payment")
    if id is not int:
        id = request.user.id
    order = Order.objects.get(
        id=id
    )
    print(f"number: {request.data.get("number")}")
    print(f"name: {request.data.get("name")}")
    print(f"month: {request.data.get("month")}")
    print(f"year: {request.data.get("year")}")
    print(f"code: {request.data.get("code")}")

    payment = Payment(
        order=order,
        card_number=request.data.get("number"),
        card_name=request.data.get("name"),
        card_month=request.data.get("month"),
        card_year=request.data.get("year"),
        card_code=request.data.get("code"),
        amount=order.total_cost
    )
    payment.save()
    print("Payment success")

    return Response(status=200)


@api_view(["GET", "POST"])
def payment_someone_view(request):
    print("its payment someone")
    pass
