from rest_framework import serializers

from catalog.models import Product, Tag, ProductImage, Specification, Review, Category, Sale


class ImageSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['src', 'alt']

    def get_src(self, obj):
        if obj.image:
            return obj.image.url
        return ''


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.CharField(source='author_name')
    rate = serializers.IntegerField()
    date = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = ['author', 'email', 'text', 'rate', 'date']

    def get_date(self, obj):
        """Форматирование даты как в API"""
        return obj.created_at.strftime('%Y-%m-%d %H:%M')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        flied = ["name", "value"]


class ProductShortSerializer(serializers.ModelSerializer):
    date = serializers.CharField()
    freeDelivery = serializers.BooleanField(source="free_delivery")
    reviews = serializers.IntegerField(source='reviews_count')
    images = ImageSerializer(many=True, source='images')
    tags = TagSerializer(many=True)

    class Meta:
        model = Product
        fields = [
            "id", "category", "price", "count", "date", "title", "description", "freeDelivery", "images", "tags",
            "reviews", "rating"
        ]


class ProductFullSerializer(serializers.ModelSerializer):
    date = serializers.CharField()
    freeDelivery = serializers.BooleanField(source="free_delivery")
    reviews = serializers.IntegerField(source='reviews')
    images = ImageSerializer(many=True, source='images')
    tags = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "category", "price", "count", "date", "title", "description", "freeDelivery", "images", "tags",
            "reviews", "rating"
        ]

    def get_tags(self, obj):
        """В ProductFull tags - массив ID тегов (не объектов!)"""
        return [tag.id for tag in obj.tags.all()]


class CatalogItemSerializer(serializers.ModelSerializer):
    image = ImageSerializer()
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "title", "image", "subcategories"]

    def get_subcategories(self, obj):
        subcategories = obj.children.filter(is_active=True)
        serializer = CatalogItemSerializer(subcategories, many=True)
        return serializer.data


class SaleItemSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='product.id')
    price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2)
    salePrice = serializers.DecimalField(source='sale_price', max_digits=10, decimal_places=2)
    dateFrom = serializers.CharField(source='dateFrom')
    dateTo = serializers.CharField(source='dateTo')
    title = serializers.CharField(source='product.title')
    images = serializers.SerializerMethodField()

    class Meta:
        model = Sale
        fields = ["id", "price", "salePrice", "dateFrom", "dateTo", "title", "images"]

    def get_images(self, obj):
        images = obj.product.images.all()
        return ImageSerializer(images, many=True).data


class CatalogResponseSerializer(serializers.Serializer):
    """Для ответа /catalog с пагинацией"""
    items = ProductShortSerializer(many=True)
    currentPage = serializers.IntegerField()
    lastPage = serializers.IntegerField()


class SalesResponseSerializer(serializers.Serializer):
    """Для ответа /sales с пагинацией"""
    items = SaleItemSerializer(many=True)
    currentPage = serializers.IntegerField()
    lastPage = serializers.IntegerField()
