from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    path('product-code/', ProductByCode.as_view()), # Get product by code!
    # Input
    path('input/<int:pk>/', ProductInputDetail.as_view(), name='input-detail'), # returns one input by ID
    # Output
    path('output/<int:pk>/', ProductOutputtDetail.as_view(), name='output-detail'), # returns one output by ID | Updates
]