from rest_framework import serializers
from .models import Product, Tag, ProductImage, Specification, Review, Category, Sale


class ImageSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()
    alt = serializers.CharField()

    class Meta:
        model = ProductImage
        fields = ['src', 'alt']

    def get_src(self, obj):
        if obj.image:
            filename = obj.image.name
            return f"/static/{filename}"
        return "/static/products/placeholder.jpg"


class ReviewSerializer(serializers.ModelSerializer):
    rate = serializers.IntegerField()
    date = serializers.SerializerMethodField()
    email = serializers.EmailField()
    author = serializers.CharField()

    class Meta:
        model = Review
        fields = ['author', 'email', 'text', 'rate', 'date']

    def get_date(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ["name", "value"]


class ProductShortSerializer(serializers.ModelSerializer):
    date = serializers.CharField()
    freeDelivery = serializers.BooleanField(source="free_delivery")
    reviews = serializers.IntegerField(source='reviews_count')
    images = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    price = serializers.FloatField()

    class Meta:
        model = Product
        fields = [
            "id", "category", "price", "count", "date", "title", "description", "freeDelivery", "images", "tags",
            "reviews", "rating"
        ]

    def get_images(self, obj):
        images = obj.images.all()
        return ImageSerializer(images, many=True).data


class ProductFullSerializer(serializers.ModelSerializer):
    date = serializers.CharField()
    freeDelivery = serializers.BooleanField(source="free_delivery")
    reviews = ReviewSerializer(many=True)
    images = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    specifications = SpecificationSerializer(many=True)
    fullDescription = serializers.CharField(source="full_description")

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
    image = serializers.SerializerMethodField()
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "title", "image", "subcategories"]

    def get_image(self, obj):
        if obj.image:
            filename = obj.image.name
            return {
                "src": f"/{filename}",
                "alt": obj.title
            }
        return {
            "src": "/static/categories/placeholder.jpg",
            "alt": obj.title
        }

    def get_subcategories(self, obj):
        subcategories = obj.children.filter(is_active=True)
        serializer = CatalogItemSerializer(subcategories, many=True)
        return serializer.data


class SaleItemSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='product.id')
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, coerce_to_string=False)
    salePrice = serializers.DecimalField(source='sale_price', max_digits=10, decimal_places=2, coerce_to_string=False)
    dateFrom = serializers.CharField()
    dateTo = serializers.CharField()
    title = serializers.CharField(source='product.title')
    images = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = ["id", "price", "salePrice", "dateFrom", "dateTo", "title", "images"]

    def get_images(self, obj):
        images = obj.product.images.all()
        return ImageSerializer(images, many=True).data
