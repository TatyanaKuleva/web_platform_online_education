from rest_framework import serializers
from rest_framework.serializers import ModelSerializer, SerializerMethodField

from users.models import Payment, User


class PaymentSerializer(ModelSerializer):

    class Meta:
        model = Payment
        fields = "__all__"


class UserSerializer(ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    payments_of_user = SerializerMethodField()

    def get_payments_of_user(self, obj):
        payments = Payment.objects.filter(user=obj)
        serializer = PaymentSerializer(payments, many=True)
        return serializer.data

    class Meta:
        model = User
        fields = "__all__"
