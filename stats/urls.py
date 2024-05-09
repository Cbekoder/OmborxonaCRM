from django.urls import path
from .views import *
from product.views import *


urlpatterns = [
    path('report/', ReportAPIView.as_view(), name='report'),
    path('inputlist/', ProductInputAPIView.as_view(), name='product-inputs'),
    path('outputlist/', ProductOutputAPIView.as_view(), name='product-outputs'),
]