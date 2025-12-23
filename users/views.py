from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets

from users.models import Payment, User

from .serializers import PaymentSerializer, UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ("lesson", "course", "payment_method")
    ordering_fields = ("payment_date",)
    search_fields = ("user__id",)
