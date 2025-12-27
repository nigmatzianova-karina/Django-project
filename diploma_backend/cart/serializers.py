from rest_framework import serializers
from .models import Cart, CartItem
from catalog.serializers import ImageSerializer, TagSerializer

class CartItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="product.id")
    category = serializers.IntegerField(source="product.category.id")
    price = serializers.FloatField(source="product.price")
    count = serializers.IntegerField(source="quantity")
    date = serializers.DateTimeField(source="added_at", format='%a %b %d %Y %H:%M:%S GMT%z')
    title = serializers.CharField(source="product.title")
    description = serializers.CharField(source="product.description")
    freeDelivery = serializers.BooleanField(source="product.free_delivery")
    reviews = serializers.IntegerField(source="product.reviews_count")
    rating = serializers.FloatField(source="product.rating")

    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["id", "category", "price", "count", "date", "title", "description",
                  "freeDelivery", "images", "tags", "reviews", "rating"]

    def get_images(self, obj):
        images = obj.product.images.all()
        return ImageSerializer(images, many=True).data

    def get_tags(self, obj):
        tags = obj.product.tags.all()
        return TagSerializer(tags, many=True).data


class CartSerializer(serializers.ListSerializer):
    """
    ListSerializer для работы со списком items
    """

    child = CartItemSerializer()

    def to_representation(self, cart):
        # cart - это объект Cart, а не список
        items = cart.items.all()
        return super().to_representation(items)

    @classmethod
    def many_init(cls, *args, **kwargs):
        # Переопределяем, чтобы принимать объект Cart
        return cls(*args, **kwargs)

