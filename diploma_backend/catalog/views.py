from decimal import Decimal, InvalidOperation
from django.db.models import Count, Prefetch
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Category, Product, Sale, Tag, Review
from .serializers import (
    CatalogItemSerializer, ProductShortSerializer, SaleItemSerializer,
    TagSerializer, ProductFullSerializer, ReviewSerializer
)


@api_view(["GET"])
def categories_view(request):
    """
    Returns a tree of active root categories with their subcategories.
    Optimized with prefetch_related for the nested structure.
    """
    categories = Category.objects.filter(
        parent__isnull=True,
        is_active=True
    ).prefetch_related('children')
    serializer = CatalogItemSerializer(categories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def catalog_view(request):
    """
    Returns a paginated list of active products with advanced filtering and sorting.
    Filters: category, name, price range, free delivery, tags.
    Sorting: rating, price, reviews count, creation date.
    """
    products = ((Product.objects.filter(is_active=True).select_related('category')
                 .prefetch_related('images', 'tags'))
                .annotate(rcount=Count('reviews')))

    if category_id := request.GET.get("category"):
        products = products.filter(category_id=category_id)

    if name_filter := request.GET.get("filter[name]"):
        products = products.filter(title__icontains=name_filter)

    try:
        if min_price := request.GET.get("filter[minPrice]"):
            products = products.filter(price__gte=Decimal(min_price))
        if max_price := request.GET.get("filter[maxPrice]"):
            products = products.filter(price__lte=Decimal(max_price))
    except (InvalidOperation, ValueError):
        pass

    if free_delivery := request.GET.get("filter[freeDelivery]"):
        products = products.filter(free_delivery=(free_delivery.lower() == "true"))

    if tags_param := request.GET.getlist('tags[]'):
        tag_ids = [int(tag_id) for tag_id in tags_param]
        products = products.filter(tags__id__in=tag_ids).distinct()

    sort_type = request.GET.get("sort", "rating")
    order = request.GET.get("order", "desc")

    sort_mapping = {
        "rating": "rating",
        "price": "price",
        "reviews": "rcount",
        "date": "created_at"
    }

    sort_field = sort_mapping.get(sort_type, "rating")
    prefix = "" if order == "asc" else "-"
    products = products.order_by(f"{prefix}{sort_field}")

    paginator = PageNumberPagination()
    paginator.page_size = int(request.GET.get("limit", 20))
    paginated_products = paginator.paginate_queryset(products, request)

    serializer = ProductShortSerializer(paginated_products, many=True)

    return Response({
        "items": serializer.data,
        "currentPage": paginator.page.number,
        "lastPage": paginator.page.paginator.num_pages
    })


@api_view(["GET"])
def popular_products_view(request):
    """
    Returns the top 8 popular products based on sort index and purchase count.
    """
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related(
        'images', 'tags'
    ).order_by("-sort_index", "-purchases_count")[:8]

    serializer = ProductShortSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def limited_products_view(request):
    """
    Returns the latest 16 limited edition products.
    """
    products = Product.objects.filter(is_active=True, limited_edition=True).select_related('category').prefetch_related(
        'images', 'tags'
    ).order_by("-created_at")[:16]

    serializer = ProductShortSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def sales_view(request):
    """
    Returns current active sales with pagination.
    """
    today = timezone.now().date()

    sales = Sale.objects.filter(
        date_from__lte=today,
        date_to__gte=today,
        product__is_active=True
    ).select_related('product').prefetch_related('product__images')

    paginator = PageNumberPagination()
    paginator.page_size = 20
    paginated_sales = paginator.paginate_queryset(sales, request)

    serializer = SaleItemSerializer(paginated_sales, many=True)
    return Response({
        "items": serializer.data,
        "currentPage": paginator.page.number,
        "lastPage": paginator.page.paginator.num_pages
    })


@api_view(["GET"])
def banners_view(request):
    """
    Returns up to 5 products designated for the home page banner.
    """
    products = Product.objects.filter(is_active=True, is_banner=True).select_related('category').prefetch_related(
        'images', 'tags'
    ).order_by('banner_order')[:5]

    serializer = ProductShortSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def tags_view(request):
    """
    Returns a list of all available product tags.
    """
    return Response(TagSerializer(Tag.objects.all(), many=True).data)


@api_view(["GET"])
def products_by_id_view(request, id):
    """
    Returns detailed information about a single product, including full description and reviews.
    """
    try:
        product = Product.objects.select_related('category').prefetch_related(
            'images', 'tags', 'specifications',
            Prefetch('reviews', queryset=Review.objects.select_related('author'))
        ).get(id=id, is_active=True)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    return Response(ProductFullSerializer(product).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def products_reviews_view(request, id):
    """
    Creates a new review for a product.
    Ensures that authenticated users can only leave one review per product.
    Automatically triggers product rating update.
    """
    try:
        product = Product.objects.get(id=id, is_active=True)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)

    if Review.objects.filter(product=product, author=request.user).exists():
        return Response({"error": "You have already reviewed this product"}, status=400)

    Review.objects.create(
        product=product,
        author=request.user,
        author_name=request.user.get_full_name() or request.user.username,
        email=request.data.get("email", request.user.email),
        text=request.data.get("text"),
        rate=request.data.get("rate"),
    )

    reviews = product.reviews.select_related('author').all()
    return Response(ReviewSerializer(reviews, many=True).data, status=201)
