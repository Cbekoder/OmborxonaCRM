from django.urls import path
from .views import *
from product.views import *


urlpatterns = [
    path('report/', ReportAPIView.as_view(), name='report'),
    # path('inputlist/', ProductInputAPIView.as_view(), name='product-inputs'),
    # INput
    path('inputs/', ProductInputList.as_view(), name='input-list'), # returns all inputs and creates new input
    path('<int:product_id>/inputs/', ProductInputListByProduct.as_view(), name='product-inputs-by-product'), # returns all inputs of one product by ID
    # Output
    path('outputs/', ProductOutputList.as_view(), name='output-list'), # returns all outputs
    path('<int:product_id>/outputs/', ProductOutputListByProduct.as_view(), name='product-outputs-by-product'), # returns all outputs of one product by ID
]