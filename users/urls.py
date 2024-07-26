from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('reporter-token/', ReporterTokenView.as_view(), name='reporter_token'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('omborchilar/', OmborchiAPIView.as_view()),
    path('omborchi/new/', OmborchiCreateAPIView.as_view()),
    path('omborchi/update/<int:pk>', OmborchiUpdateAPIView.as_view(), name='omborchi-update'),
    path('omborchi/detail/', OmborchiDetailAPIView.as_view(), name='omborchi-detail'),
    path('report-code/', ReportCodeView.as_view(), name='report-code'),
]
