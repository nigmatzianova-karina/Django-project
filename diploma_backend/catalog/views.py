from decimal import Decimal

from rest_framework.decorators import api_view, permission_classes
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from catalog.models import Category, Product, Sale, Tag, Review
from catalog.serializers import (CatalogItemSerializer, ProductShortSerializer, SaleItemSerializer, TagSerializer,
                                 ProductFullSerializer, ReviewSerializer)


@api_view(["GET"])
def categories_view(request):
    categories = Category.objects.filter(
        parent__isnull=True,
        is_active=True
    )
    serializer = CatalogItemSerializer(categories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def catalog_view(request):
    products = Product.objects.filter(is_active=True)
    print("all products")
    print(products)

    if category_id := request.GET.get("category"):
        products = products.filter(category_id=category_id)
        print("filter by category")
        print(products)

    if name_filter := request.GET.get("filter[name]"):
        products = products.filter(title__icontains=name_filter)
        print("filter by name")
        print(products)

    if min_price := request.GET.get("filter[minPrice]"):
        products = products.filter(price__gte=Decimal(min_price))
        print("filter by min price")
        print(products)

    if max_price := request.GET.get("filter[maxPrice]"):
        products = products.filter(price__lte=Decimal(max_price))
        print("filter by max price")
        print(products)

    if free_delivery := request.GET.get("filter[freeDelivery]"):
        products = products.filter(free_delivery=(free_delivery.lower() == "true"))
        print("filter by free delivery")
        print(products)

    sort_type = request.GET.get("sort", "rating")
    order = request.GET.get("order", "desc")

    sort_mapping = {
        "rating": "rating",
        "price": "price",
        "reviews": "reviews_count",
        "date": "created_at"
    }

    sort_field = sort_mapping.get(sort_type, "rating")

    if order == "asc":
        sort_field = sort_field
    else:
        sort_field = f"-{sort_field}"

    products = products.order_by(sort_field)
    print(f"ordering by {sort_field}")
    print(products)

    paginator = PageNumberPagination()
    paginator.page_size = int(request.GET.get("limit", 20))
    paginated_products = paginator.paginate_queryset(products, request)

    serializer = ProductShortSerializer(paginated_products, many=True)
    print("pass serializer")
    print("\npaginated_products\n")
    print(paginated_products)
    response_data = {
        "items": serializer.data,
        "currentPage": paginator.page.number,
        "lastPage": paginator.page.paginator.num_pages
    }

    print("=== RESPONSE DATA ===")
    import json
    print(json.dumps(response_data, indent=2, default=str))
    print("=====================")

    return Response(response_data)

@api_view(["GET"])
def popular_products_view(request):
    products = Product.objects.filter(
        is_active=True
    ).order_by("-sort_index", "-purchases_count")[:8]

    serializer = ProductShortSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def limited_products_view(request):
    products = Product.objects.filter(
        is_active=True,
        limited_edition=True
    ).order_by("-created_at")[:16]

    serializer = ProductShortSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def sales_view(request):
    from django.utils import timezone
    today = timezone.now().date()

    sales = Sale.objects.filter(
        date_from__lte=today,
        date_to__gte=today,
        product__is_active=True
    )

    paginator = PageNumberPagination()
    paginator.page_size = 20
    paginated_sales = paginator.paginate_queryset(sales, request)

    serializer = SaleItemSerializer(paginated_sales, many=True)

    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
def banners_view(request):
    products = Product.objects.filter(
        is_active=True,
        is_banner=True
    ).order_by('banner_order')[:5]

    serializer = ProductShortSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def tags_view(request):
    tags = Tag.objects.all()
    serializer = TagSerializer(tags, many=True)

    return Response(serializer.data)


@api_view(["GET"])
def products_by_id_view(request, id):
    try:
        product = Product.objects.get(id=id, is_active=True)
    except Product.DoesNotExist:
        return Response({"error": "Does not exist"}, status=404)

    serializer = ProductFullSerializer(product)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def products_reviews_view(request, id):
    try:
        product = Product.objects.get(id=id, is_active=True)
    except Product.DoesNotExist:
        return Response({"error": "Does not exist"}, status=404)

    if Review.objects.filter(product=product, author=request.user):
        return Response({"error": ""}, status=400)

    review = Review.objects.create(
        product=product,
        author=request.user,
        text=request.data.get("text"),
        rate=request.data.get("rate")
    )

    product.update_rating()

    reviews = product.reviews.all()
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data, status=201)
