from django.urls import path
from .views import *
from product.views import *


urlpatterns = [
    path('report/', ReportAPIView.as_view(), name='report'),
    # Input
    path('inputs/', ProductInputsListAPIView.as_view(), name='input-list'),
    # Output
    path('outputs/', ProductOutputsListAPIView.as_view(), name='output-list'),
]