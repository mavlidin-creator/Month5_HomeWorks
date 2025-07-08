from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListView.as_view()),
    path('categories/<int:id>/', views.CategoryDetailView.as_view()),

    path('products/', views.ProductListView.as_view()),
    path('products/<int:id>/', views.ProductDetailView.as_view()),

    path('reviews/', views.ReviewListView.as_view()),
    path('reviews/<int:id>/', views.ReviewDetailView.as_view()),
]
