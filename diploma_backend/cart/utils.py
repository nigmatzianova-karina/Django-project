from .models import Cart, CartItem
from catalog.models import Product

def merge_cart_after_login(request, user):
    """
    Transfers items from an anonymous session to the user's database.
    """
    session_cart_data = request.session.get('cart', {})
    if not session_cart_data:
        return

    db_cart, _ = Cart.objects.get_or_create(user=user)

    for p_id, item_info in session_cart_data.items():
        try:
            product = Product.objects.get(id=p_id)
            qty = item_info.get('quantity', 0)

            item, created = CartItem.objects.get_or_create(
                cart=db_cart,
                product=product,
                defaults={'quantity': qty}
            )
            if not created:
                item.quantity += qty
                item.save()
        except Product.DoesNotExist:
            continue

    del request.session['cart']
    request.session.modified = True
