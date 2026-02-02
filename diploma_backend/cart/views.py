from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Prefetch
from catalog.models import Product
from .serializers import CartSerializer
from .models import Cart, CartItem


@api_view(["GET", "POST", "DELETE"])
def basket_view(request):
    """
    Main endpoint for shopping cart management.
    Supports retrieving the cart, adding items, and removing/decreasing item quantity.
    Handles both authenticated users and guest sessions.
    """
    cart_queryset = Cart.objects.prefetch_related(
        Prefetch(
            'items',
            queryset=CartItem.objects.select_related('product').prefetch_related(
                'product__images',
                'product__tags'
            )
        )
    )

    if request.user.is_authenticated:
        cart, _ = cart_queryset.get_or_create(user=request.user)
    else:
        cart, _ = cart_queryset.get_or_create(
            session_key=request.session.session_key,
            user=None
        )

    if request.method == "GET":
        return Response(CartSerializer(cart).data)

    elif request.method == "POST":
        product_id = request.data.get("id")
        quantity = int(request.data.get("count", 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity}
        )

        if not created:
            item.quantity += quantity
            item.save()

        return Response(CartSerializer(cart).data)

    elif request.method == "DELETE":
        product_id = request.data.get("id")
        quantity = int(request.data.get("count", 1))

        try:
            item = CartItem.objects.get(cart=cart, product_id=product_id)

            if item.quantity > quantity:
                item.quantity -= quantity
                item.save()
            else:
                item.delete()

        except CartItem.DoesNotExist:
            return Response({"error": "Item not found in cart"}, status=404)

        return Response(CartSerializer(cart).data)

    return Response(status=400)
