from rest_framework import serializers
from catalog.models import Product, Tag, ProductImage, Specification, Review, Category, Sale


class ImageSerializer(serializers.ModelSerializer):
    src = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['src', 'alt']

    def get_src(self, obj):
        src = "/static/products/placeholder.jpg"
        alt = obj.title or "No image"

        if obj.image:
            if hasattr(obj.image, 'url'):
                url = obj.image.url
                if '/products/' in url:
                    filename = url.split('/products/')[-1]
                    src = f"/static/products/{filename}"
                else:
                    filename = url.split('/')[-1]
                    src = f"/static/products/{filename}"

            elif hasattr(obj.image, 'name'):
                file_name = obj.image.name
                if '/products/' in file_name:
                    filename = file_name.split('/products/')[-1]
                    src = f"/static/products/{filename}"
                else:
                    filename = file_name.split('/')[-1]
                    src = f"/static/products/{filename}"

            elif isinstance(obj.image, str):
                if obj.image.startswith('/'):
                    src = obj.image
                elif obj.image.startswith('static/'):
                    src = '/' + obj.image
                else:
                    src = f"/static/products/{obj.image}"

        if not src.startswith('/'):
            src = '/' + src

        return {
            "src": src,
            "alt": alt
        }


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
    reviews = ReviewSerializer(source="reviews.all")
    images = serializers.SerializerMethodField()
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
        src = "/static/categories/placeholder.jpg"
        alt = obj.title or "No image"

        if obj.image:
            if hasattr(obj.image, 'url'):
                url = obj.image.url
                if '/categories/' in url:
                    filename = url.split('/categories/')[-1]
                    src = f"/static/categories/{filename}"
                else:
                    filename = url.split('/')[-1]
                    src = f"/static/categories/{filename}"

            elif hasattr(obj.image, 'name'):
                file_name = obj.image.name
                if '/categories/' in file_name:
                    filename = file_name.split('/categories/')[-1]
                    src = f"/static/categories/{filename}"
                else:
                    filename = file_name.split('/')[-1]
                    src = f"/static/categories/{filename}"

            elif isinstance(obj.image, str):
                if obj.image.startswith('/'):
                    src = obj.image
                elif obj.image.startswith('static/'):
                    src = '/' + obj.image
                else:
                    src = f"/static/categories/{obj.image}"

        if not src.startswith('/'):
            src = '/' + src

        return {
            "src": src,
            "alt": alt
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
