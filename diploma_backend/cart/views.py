from rest_framework.decorators import api_view
from rest_framework.response import Response
from catalog.models import Product
from .serializers import CartSerializer
from .models import Cart, CartItem


@api_view(["GET", "POST", "DELETE"])
def basket_view(request):
    if not request.session.session_key:
        request.session.create()

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
    else:
        cart, _ = Cart.objects.get_or_create(
            session_key=request.session.session_key,
            user=None
        )

    if request.method == "GET":
        return Response(CartSerializer(cart).data)

    elif request.method == "POST":
        try:
            product = Product.objects.get(
                id=request.data.get("id")
            )
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        quantity = int(request.data.get("count", 1))

        try:
            item = CartItem.objects.get(
                cart=cart,
                product=product,
            )
            item.quantity += quantity
            item.save()
            print("Item already in cart")
        except CartItem.DoesNotExist:
            print("Item created")
            item = CartItem.objects.create(
                cart=cart,
                product=product,
                quantity=quantity
            )

        cart.save()

        return Response(CartSerializer(cart).data)

    elif request.method == "DELETE":
        try:
            product = Product.objects.get(
                id=request.data.get("id")
            )
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        quantity = int(request.data.get("count", 1))

        try:
            item = CartItem.objects.get(
                cart=cart,
                product=product,
            )
            if current_quantity := item.quantity - quantity:
                print(f"current_quantity: {current_quantity}")
                print(f"item quantity: {item.quantity}")
                item.quantity = current_quantity
                item.save()
            else:
                item.delete()
        except CartItem.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)
        return Response(data=["success"], status=200)
    return Response(status=400)
