from django.conf import settings
from rest_framework import serializers
from .models import Product, Tag, ProductImage, Specification, Review, Category, Sale

class ImageSerializer(serializers.ModelSerializer):
    """
    Serializes ProductImage model into a frontend-friendly format.
    Provides absolute or relative source paths for images.
    """
    src = serializers.SerializerMethodField()
    alt = serializers.CharField()

    def get_src(self, obj):
        """Standardizes image output for products."""
        if obj.image:
            return f"{settings.STATIC_URL}{obj.image.name}"
        return "/static/products/placeholder.jpg"

    class Meta:
        model = ProductImage
        fields = ['src', 'alt']


class ReviewSerializer(serializers.ModelSerializer):
    """
    Converts Product reviews into JSON.
    Handles date formatting and provides author details.
    """
    date = serializers.DateTimeField(source='created_at', format='%Y-%m-%d %H:%M')
    author = serializers.CharField(source='author.username', default='Anonymous')

    class Meta:
        model = Review
        fields = ['author', 'email', 'text', 'rate', 'date']


class TagSerializer(serializers.ModelSerializer):
    """Serializes tags"""
    class Meta:
        model = Tag
        fields = ["id", "name"]


class SpecificationSerializer(serializers.ModelSerializer):
    """Serializes specification"""
    class Meta:
        model = Specification
        fields = ["name", "value"]


class ProductShortSerializer(serializers.ModelSerializer):
    """
    A lightweight version of the Product serializer for catalog listing.
    Optimized for performance by excluding heavy fields.
    """
    date = serializers.DateTimeField(source="created_at", format='%a %b %d %Y %H:%M:%S GMT%z', read_only=True)
    freeDelivery = serializers.BooleanField(source="free_delivery", read_only=True)
    reviews = serializers.IntegerField(source='rcount', read_only=True)
    images = ImageSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = [
            "id", "category", "price", "count", "date", "title",
            "description", "freeDelivery", "images", "tags", "reviews", "rating"
        ]


class ProductFullSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(source="created_at", format='%a %b %d %Y %H:%M:%S GMT%z', read_only=True)
    freeDelivery = serializers.BooleanField(source="free_delivery", read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)
    specifications = SpecificationSerializer(many=True, read_only=True)
    fullDescription = serializers.CharField(source="full_description", read_only=True)


    class Meta:
        model = Product
        fields = [
            "id", "category", "price", "count", "date", "title", "description", "fullDescription", "freeDelivery",
            "images", "tags", "reviews", "specifications", "rating"
        ]

    def get_images(self, obj):
        images = obj.images.all()
        return ImageSerializer(images, many=True).data


class CatalogItemSerializer(serializers.ModelSerializer):
    """
    Recursive serializer for Categories and their children.
    Enables deep nesting of subcategories for the main menu.
    """
    image = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "title", "image", "subcategories"]

    def get_image(self, obj):
        """Standardizes image output for categories."""
        if obj.image:
            return {"src": f"{settings.STATIC_URL}{obj.image.name}", "alt": obj.title}
        return {"src": "/static/categories/placeholder.jpg", "alt": obj.title}

    def get_subcategories(self, obj):
        """Fetch active child categories recursively."""
        subcategories = obj.children.filter(is_active=True)
        return CatalogItemSerializer(subcategories, many=True).data


class SaleItemSerializer(serializers.ModelSerializer):
    """
    Serializer for promotional products with old and new prices.
    Used for the 'Sales' page or special offers block.
    """
    id = serializers.IntegerField(source='product.id')
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)
    salePrice = serializers.DecimalField(source='sale_price', max_digits=10, decimal_places=2)
    dateFrom = serializers.CharField(source='date_from')
    dateTo = serializers.CharField(source='date_to')
    title = serializers.CharField(source='product.title')
    images = ImageSerializer(source='product.images', many=True, read_only=True)

    class Meta:
        model = Sale
        fields = ["id", "price", "salePrice", "dateFrom", "dateTo", "title", "images"]
