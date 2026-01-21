from rest_framework import serializers
from orders.models import Order, OrderItem
from catalog.serializers import ImageSerializer, TagSerializer


class OrderSerializer(serializers.ModelSerializer):
    createdAt = serializers.CharField(source="created_at")
    fullName = serializers.CharField(source="full_name")
    deliveryType = serializers.CharField(source="delivery_type")
    paymentType = serializers.CharField(source="payment_type")
    totalCost = serializers.DecimalField(source="total_cost",max_digits=12, decimal_places=2)
    products = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "createdAt", "fullName", "email", "phone", "deliveryType", "paymentType",
                  "totalCost", "status", "city", "address", "products"]

    def get_products(self, obj):
        products = obj.items.all()
        return OrderProductSerializer(products, many=True).data


class OrderProductSerializer(serializers.ModelSerializer):
    category = serializers.IntegerField(source="product.category.id")
    price = serializers.FloatField(source="product.price")
    count = serializers.IntegerField(source="quantity")
    date = serializers.DateTimeField(source="order.created_at", format='%a %b %d %Y %H:%M:%S GMT%z')
    title = serializers.CharField(source="product.title")
    description = serializers.CharField(source="product.description")
    freeDelivery = serializers.BooleanField(source="product.free_delivery")
    reviews = serializers.IntegerField(source="product.reviews_count")
    rating = serializers.FloatField(source="product.rating")

    images = serializers.SerializerMethodField()
    tags = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "category", "price", "count", "date", "title", "description", "freeDelivery", "images",
                  "tags", "reviews", "rating"]

    def get_images(self, obj):
        images = obj.product.images.all()
        return ImageSerializer(images, many=True).data

    def get_tags(self, obj):
        tags = obj.product.tags.all()
        return TagSerializer(tags, many=True).data