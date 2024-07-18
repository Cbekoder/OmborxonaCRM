from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserSerializer, UserCreateSerializer, ReportCodeSerializer, UserListSerializer, \
    UserUpdateSerializer, OmborchiDetailSerializer
from .permissions import *
from .models import *


class OmborchiAPIView(APIView):
    permission_classes = (IsBuxgalterUser,)

    @swagger_auto_schema(tags=['Omborchi'])
    def get(self, request):
        users = User.objects.filter(position=1)
        user_serializer = UserListSerializer(users, many=True)
        return Response(user_serializer.data)


class OmborchiCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsBuxgalterUser]

    @swagger_auto_schema(tags=['Omborchi'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class OmborchiUpdateAPIView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [CanUpdateOmborchi]

    @swagger_auto_schema(tags=['Omborchi'])
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @swagger_auto_schema(tags=['Omborchi'])
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)


class OmborchiDetailAPIView(APIView):
    permission_classes = [CanUpdateOmborchi]

    @swagger_auto_schema(tags=['Omborchi'],
                         manual_parameters=[
                             openapi.Parameter(
                                 'id',
                                 openapi.IN_QUERY,
                                 description="Omborchi ID (Faqat Buxgalter user uchun)",
                                 type=openapi.TYPE_INTEGER,
                                 required=False
                             )
                         ])
    def get(self, request):
        # Check if the user is an Omborchi
        if IsOmborchiUser().has_permission(request, self):
            user = request.user
        # Check if the user is a Buxgalter
        elif IsBuxgalterUser().has_permission(request, self):
            user_id = request.query_params.get('id', None)
            if not user_id:
                return Response({"error": "Buxgalter uchun Omborchi ID kiritish majburiy."}, status=400)
            try:
                user = User.objects.get(id=user_id, position=1)  # Assuming position=1 is for Omborchi
            except User.DoesNotExist:
                return Response({"error": "Berilgan ID bo'yicha Omborchi topilmadi."}, status=404)
        else:
            return Response({"error": "Unauthro"}, status=403)

        user_serializer = OmborchiDetailSerializer(user)
        return Response(user_serializer.data)


class ReportCodeView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsBuxgalterUser]

    @swagger_auto_schema(tags=['Password for report'])
    def get(self, request):
        code = ReportCode.objects.last()
        serializer = ReportCodeSerializer(code)
        return Response(serializer.data)

    @swagger_auto_schema(tags=['Password for report'], request_body=ReportCodeSerializer)
    def put(self, request):
        code = ReportCode.objects.last()
        serializer = ReportCodeSerializer(code, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReporterTokenView(APIView):
    @swagger_auto_schema(tags=['user'], request_body=ReportCodeSerializer)
    def post(self, request):
        serializer = ReportCodeSerializer(data=request.data)
        if serializer.is_valid():
            password = request.data.get("password")
            last_password = ReportCode.objects.last().password
            if password == last_password:
                user = User.objects.get(username="reporter")
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                # refresh_token = str(refresh)
                return JsonResponse({
                    'access_token': access_token,
                    # 'refresh_token': refresh_token
                })
            return Response({"error": "Wrong password"}, status=400)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
