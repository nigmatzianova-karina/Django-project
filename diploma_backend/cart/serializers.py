from rest_framework import serializers
from .models import Cart, CartItem
from catalog.serializers import ImageSerializer, TagSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """
    Serializer for individual items within a shopping cart.
    Transforms CartItem model data into the format expected by the frontend catalog components.

    Attributes:
        count: Maps to 'quantity' in the model.
        date: Formatted addition timestamp for frontend compatibility.
    """
    id = serializers.IntegerField(source="product.id", read_only=True)
    category = serializers.IntegerField(source="product.category.id", read_only=True)
    price = serializers.FloatField(source="product.price", read_only=True)
    count = serializers.IntegerField(source="quantity")
    date = serializers.DateTimeField(source="added_at", format='%a %b %d %Y %H:%M:%S GMT%z', read_only=True)
    title = serializers.CharField(source="product.title", read_only=True)
    description = serializers.CharField(source="product.description", read_only=True)
    freeDelivery = serializers.BooleanField(source="product.free_delivery", read_only=True)
    reviews = serializers.IntegerField(source="product.reviews_count", read_only=True)
    rating = serializers.FloatField(source="product.rating", read_only=True)

    images = ImageSerializer(source="product.images", many=True, read_only=True)
    tags = TagSerializer(source="product.tags", many=True, read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id", "category", "price", "count", "date", "title",
            "description", "freeDelivery", "images", "tags", "reviews", "rating"
        ]


class CartSerializer(serializers.ListSerializer):
    """
    Serializer for the Cart model.
    Provides a wrapped representation of the cart including its constituent items.
    """
    child = CartItemSerializer()

    def to_representation(self, data):
        if isinstance(data, Cart):
            items = data.items.all()
            return super().to_representation(items)
        return super().to_representation(data)

    @classmethod
    def many_init(cls, *args, **kwargs):
        return cls(*args, **kwargs)
