from django.urls import path
from .views import *
from product.views import *


urlpatterns = [
    path('report/', ReportAPIView.as_view(), name='report'),
    # Input
    path('inputs/', ProductInputsListAPIView.as_view(), name='input-list'),
    path('<int:product_id>/inputs/', ProductInputListByProduct.as_view(), name='product-inputs-by-product'), # returns all inputs of one product by ID
    # Output
    path('outputs/', ProductOutputsListAPIView.as_view(), name='output-list'),
    path('<int:product_id>/outputs/', ProductOutputListByProduct.as_view(), name='product-outputs-by-product'), # returns all outputs of one product by ID
]