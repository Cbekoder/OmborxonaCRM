from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


urlpatterns = [
    # catergory
    path('categories/', CategoriesAPIView.as_view(), name='categories-list-create'),
    path('category/<int:c>', CategoryAPIView.as_view(), name='category-detail-put-patch-delete'),
    # units
    path('units/', UnitsAPIView.as_view(), name='units-list-create'),
    path('units/<int:u>/', UnitAPIView.as_view(), name='unit-detail-put-patch-delete'),
    # products
    path('products/', ProductsAPIView.as_view(), name='products-list-create'),
    path('product/<int:p>', ProductAPIView.as_view(), name='product-detail-put-patch-delete'),
    path('product-code/<str:prod_code>', ProductByCode.as_view()),
    # Input
    path('input/', ProductInputsAPIView.as_view(), name='products-list-create'),
    # path('input/<int:pk>/', ProductInputDetail.as_view(), name='input-detail'), # returns one input by ID
    # Output
    path('output/', ProductOutputAPIView.as_view(), name='products-list-create'),
    # path('output/<int:pk>/', ProductOutputtDetail.as_view(), name='output-detail'), # returns one output by ID | Updates
]