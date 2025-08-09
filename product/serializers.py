from rest_framework import serializers
from .models import Category, Product, Review
from rest_framework.validators import UniqueValidator

class CategorySerializer(serializers.ModelSerializer):
    name = serializers.CharField(
        max_length=100,
        required=True,
        allow_blank=False,
        validators=[
            UniqueValidator(queryset=Category.objects.all(), message="Категория с таким названием уже существует.")
        ]
    )
    products_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'products_count')

    def validate_name(self, value):
        if len(value.strip()) < 2:
            raise serializers.ValidationError("Название категории должно быть не короче 2 символов.")
        return value


class ReviewSerializer(serializers.ModelSerializer):
    text = serializers.CharField(required=True, allow_blank=False)
    stars = serializers.IntegerField(required=True)
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)

    class Meta:
        model = Review
        fields = '__all__'  # вместо 'all'

    def validate_stars(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Оценка должна быть от 1 до 5.")
        return value

    def validate_text(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Текст отзыва должен быть не короче 10 символов.")
        return value



class ProductSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=True, allow_blank=False)
    description = serializers.CharField(required=True, allow_blank=False)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), required=True)

    reviews = ReviewSerializer(many=True, read_only=True)
    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = ('id', 'title', 'description', 'price', 'category', 'reviews', 'rating')

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            total_stars = sum([review.stars for review in reviews])
            return round(total_stars / len(reviews), 2)
        return 0.0

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Название продукта должно быть не короче 3 символов.")
        return value

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Цена не может быть отрицательной.")
        return value