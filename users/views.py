from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import UserSerializer, UserCreateSerializer
from .permissions import *
from .models import *


class OmborchiAPIView(APIView):
    def get(self, request):
        users = User.objects.filter(position=1)
        user_serializer = UserSerializer(users, many=True)
        return Response(user_serializer.data)

class OmborchiCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsBuxgalterUser]

    def perform_create(self, serializer):
        serializer.save()