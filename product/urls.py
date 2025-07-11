from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.category_list_view),
    path('categories/<int:id>/', views.category_detail_view),
    path('products/', views.product_list_view),
    path('products/<int:id>/', views.product_detail_view),
    path('products/reviews/', views.product_reviews_list_view),
    path('reviews/', views.review_list_view),
    path('reviews/<int:id>/', views.review_detail_view),
]