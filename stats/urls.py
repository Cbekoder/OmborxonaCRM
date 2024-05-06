from django.urls import path
from .views import *


urlpatterns = [
    path('report/', ReportAPIView.as_view(), name='report'),
]