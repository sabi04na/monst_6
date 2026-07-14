from collections import OrderedDict
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from common.validators import validate_age_from_token

from .permissions import IsModerator
from common.validators import validate_age_from_token

from .models import Category, Product, Review
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ReviewSerializer,
    ProductWithReviewsSerializer,
    CategoryValidateSerializer,
    ProductValidateSerializer,
    ReviewValidateSerializer
)

PAGE_SIZE = 5


class CustomPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('total', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))

    def get_page_size(self, request):
        return PAGE_SIZE


class CategoryListCreateAPIView(ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination

    def post(self, request, *args, **kwargs):
        serializer = CategoryValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        category = Category.objects.create(**serializer.validated_data)
        return Response(data=CategorySerializer(category).data, status=status.HTTP_201_CREATED)


class CategoryDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = CategoryValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.name = serializer.validated_data['name']
        instance.save()
        return Response(data=CategorySerializer(instance).data)


class ProductListCreateAPIView(ListCreateAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):

        if request.user.is_authenticated and request.user.is_staff:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data={"error": "Модератор не может создавать продукты."}
            )

        # 2. Валидация данных продукта
        serializer = ProductValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 3. Проверка возраста (импорт уже есть вверху файла)
        from common.validators import validate_age_from_token
        validate_age_from_token(request)   # ← здесь НЕТ переменной user, только request

        # 4. Создание продукта
        product = Product.objects.create(
            title=serializer.validated_data['title'],
            description=serializer.validated_data.get('description', ''),
            price=serializer.validated_data['price'],
            category=serializer.validated_data['category']
        )

        return Response(
            data=ProductSerializer(product).data,
            status=status.HTTP_201_CREATED
        )


class ProductDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.select_related('category').all()
    serializer_class = ProductSerializer
    lookup_field = 'id'

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsModerator()]
        return [IsAuthenticatedOrReadOnly()]

    def put(self, request, *args, **kwargs):
        product = self.get_object()
        serializer = ProductValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product.title = serializer.validated_data['title']
        product.description = serializer.validated_data.get('description', '')
        product.price = serializer.validated_data['price']
        product.category = serializer.validated_data['category']
        product.save()

        return Response(data=ProductSerializer(product).data)


class ReviewViewSet(ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    pagination_class = CustomPagination
    lookup_field = 'id'

    def create(self, request, *args, **kwargs):
        serializer = ReviewValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = Review.objects.create(
            text=serializer.validated_data['text'],
            stars=serializer.validated_data['stars'],
            product=serializer.validated_data['product']
        )

        return Response(data=ReviewSerializer(review).data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        serializer = ReviewValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review.text = serializer.validated_data['text']
        review.stars = serializer.validated_data['stars']
        review.product = serializer.validated_data['product']
        review.save()

        return Response(data=ReviewSerializer(review).data)


class ProductWithReviewsAPIView(APIView):
    def get(self, request):
        paginator = CustomPagination()
        products = Product.objects.select_related('category').prefetch_related('reviews').all()
        result_page = paginator.paginate_queryset(products, request)
        serializer = ProductWithReviewsSerializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)