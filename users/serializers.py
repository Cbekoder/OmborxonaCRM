from rest_framework import serializers
from users.models import User, ReportCode


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name']
        # extra_kwargs = {
        #     # 'password': {'write_only': True},
        #     'username': {'required': False},  # Allow DRF to generate a unique username
        # }

    def create(self, validated_data):
        validated_data['position'] = 1  # Ensure position is 'omborchi'
        user = User.objects.create_user(**validated_data)
        return user

class ReportCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReportCode
        fields = ['password']
