from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('product-inputs/', ProductInputCreateAPIView.as_view(), name='product_input_create'),
    path('product-outputs/', ProductOutputCreateAPIView.as_view(), name='product_output_create'),
]