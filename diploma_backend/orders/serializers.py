from rest_framework import serializers
from orders.models import Order, OrderItem
from catalog.serializers import ImageSerializer, TagSerializer


class OrderProductSerializer(serializers.ModelSerializer):
    """
    Serializer for products within an order.
    Crucially uses historical price from OrderItem instead of the current catalog price.
    """
    id = serializers.IntegerField(source="product.id", read_only=True)
    category = serializers.IntegerField(source="product.category.id", read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2)
    count = serializers.IntegerField(source="quantity")
    date = serializers.DateTimeField(source="order.created_at", format='%a %b %d %Y %H:%M:%S GMT%z', read_only=True)
    title = serializers.CharField(source="product.title", read_only=True)
    description = serializers.CharField(source="product.description", read_only=True)
    freeDelivery = serializers.BooleanField(source="product.free_delivery", read_only=True)
    reviews = serializers.IntegerField(source="product.reviews_count", read_only=True)
    rating = serializers.FloatField(source="product.rating", read_only=True)

    images = ImageSerializer(source="product.images", many=True, read_only=True)
    tags = TagSerializer(source="product.tags", many=True, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id", "category", "price", "count", "date", "title", "description",
            "freeDelivery", "images", "tags", "reviews", "rating"
        ]


class OrderSerializer(serializers.ModelSerializer):
    """
    Full Order serializer for checkout and history views.
    Flattens Django's snake_case into frontend's camelCase.
    """
    createdAt = serializers.DateTimeField(source="created_at", format='%a %b %d %Y %H:%M:%S GMT%z', read_only=True)
    fullName = serializers.CharField(source="full_name", read_only=True)
    deliveryType = serializers.CharField(source="delivery_type", read_only=True)
    paymentType = serializers.CharField(source="payment_type", read_only=True)
    totalCost = serializers.DecimalField(source="total_cost", max_digits=12, decimal_places=2, read_only=True)
    products = OrderProductSerializer(source="items", many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "createdAt", "fullName", "email", "phone", "deliveryType",
            "paymentType", "totalCost", "status", "city", "address", "products"
        ]
