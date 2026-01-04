from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import Payment, User
from users.permissions import IsOwner, IsUserOwner

from .serializers import PaymentSerializer, UserCreateSerializer, UserPrivateSerializer, UserPublicSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()

    def get_serializer_class(self):
        user = self.request.user
        if self.action == "list":
            return UserPrivateSerializer
        elif self.action in ["retrieve", "update", "partial_update"]:
            obj = self.get_object()
            if obj.id == user.id:
                return UserPrivateSerializer
            else:
                return UserPublicSerializer

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [IsAuthenticated, IsUserOwner]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class UserCreateAPIView(CreateAPIView):
    serializer_class = UserCreateSerializer
    queryset = User.objects.all()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ("lesson", "course", "payment_method")
    ordering_fields = ("payment_date",)
    search_fields = ("user__id",)
