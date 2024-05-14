from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'units', UnitViewSet, basename='unit')
router.register(r'products', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
    # Input
    path('inputs/', ProductInputList.as_view(), name='input-list'), # returns all inputs and creates new input
    path('input/<int:pk>/', ProductInputDetail.as_view(), name='input-detail'), # returns one input by ID
    path('<int:product_id>/inputs/', ProductInputListByProduct.as_view(), name='product-inputs-by-product'), # returns all inputs of one product by ID
    # Output
    path('outputs/', ProductOutputList.as_view(), name='output-list'), # returns all outputs
    path('output/<int:pk>/', ProductOutputtDetail.as_view(), name='output-detail'), # returns one output by ID | Updates
    path('<int:product_id>/outputs/', ProductOutputListByProduct.as_view(), name='product-outputs-by-product'), # returns all outputs of one product by ID


#     path('inputs/', ProductInputDetailAPIView.as_view(), name='product_input_list'),
#     path('inputs/create', ProductInputCreateAPIView.as_view(), name='product_input_create'),
#     path('inputs/<int:pk>/', ProductInputRetrieveUpdateDestroyAPIView.as_view(), name='product_input_detail'),

#     path('outputs/', ProductOutputCreateAPIView.as_view(), name='product_output_create'),
]