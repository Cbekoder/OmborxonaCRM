from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserSerializer, UserCreateSerializer, ReportCodeSerializer, UserListSerializer, \
    UserUpdateSerializer
from .permissions import *
from .models import *


class OmborchiAPIView(APIView):
    permission_classes = (IsBuxgalterUser,)
    def get(self, request):
        users = User.objects.filter(position=1)
        user_serializer = UserListSerializer(users, many=True)
        return Response(user_serializer.data)

class OmborchiCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsBuxgalterUser]

    def perform_create(self, serializer):
        serializer.save()

class OmborchiUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserUpdateSerializer
    permission_classes = [CanUpdateOmborchi]


class ReportCodeView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsBuxgalterUser]

    def get(self, request):
        code = ReportCode.objects.last()
        serializer = ReportCodeSerializer(code)
        return Response(serializer.data)

    def put(self, request):
        code = ReportCode.objects.last()
        serializer = ReportCodeSerializer(code, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
