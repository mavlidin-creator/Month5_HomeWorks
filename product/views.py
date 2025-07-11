from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Category, Product, Review
from .serializers import CategorySerializer, ProductSerializer, ReviewSerializer
from django.shortcuts import get_object_or_404
from django.db.models import Avg

@api_view(['GET'])
def category_list_view(request):
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def category_detail_view(request, id):
    category = get_object_or_404(Category, id=id)
    serializer = CategorySerializer(category)
    return Response(serializer.data)

@api_view(['GET'])
def product_list_view(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def product_detail_view(request, id):
    product = get_object_or_404(Product, id=id)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

@api_view(['GET'])
def review_list_view(request):
    reviews = Review.objects.all()
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def review_detail_view(request, id):
    review = get_object_or_404(Review, id=id)
    serializer = ReviewSerializer(review)
    return Response(serializer.data)

@api_view(['GET'])
def product_reviews_list_view(request):
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)
