from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField
from rest_framework.validators import UniqueValidator

from users.models import Payment, User


class PaymentSerializer(ModelSerializer):

    class Meta:
        model = Payment
        fields = "__all__"


class UserPublicSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email", "avatar", "city"]


class UserPrivateSerializer(ModelSerializer):
    payments_of_user = SerializerMethodField()

    def get_payments_of_user(self, obj):
        payments = Payment.objects.filter(user=obj)
        serializer = PaymentSerializer(payments, many=True)
        return serializer.data

    class Meta:
        model = User
        fields = "__all__"


class UserCreateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password", "phone_number", "avatar", "city")
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
