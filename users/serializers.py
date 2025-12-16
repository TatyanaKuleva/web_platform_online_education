from users.models import User
from rest_framework import serializers

from rest_framework.serializers import ModelSerializer

class UserSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = '__all__'
