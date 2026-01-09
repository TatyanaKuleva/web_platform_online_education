from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema

from users.models import Payment, User
from users.permissions import IsOwner, IsUserOwner

from .serializers import PaymentSerializer, UserCreateSerializer, UserPrivateSerializer, UserPublicSerializer

@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Список пользователей (приватные данные)",
    responses={200: UserPrivateSerializer(many=True)}
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_description="Просмотр профиля. Если это ваш профиль — данных больше.",
    responses={200: UserPrivateSerializer(), 203: UserPublicSerializer()}
))

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

    @swagger_auto_schema(
        operation_summary="Регистрация нового пользователя",
        responses={201: UserCreateSerializer(), 400: "Ошибка валидации"}
    )

    def perform_create(self, serializer):
        serializer.save(is_active=True)

# @method_decorator(name='list', decorator=swagger_auto_schema(
#     operation_summary="Список платежей",
#     operation_description="Позволяет фильтровать по курсу, уроку и способу оплаты."
# ))
class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ("lesson", "course")
    # ordering_fields = ("payment_date",)
    search_fields = ("user__id",)

# class PaymentCreateAPIView(CreateAPIView):
#     serializer_class = PaymentSerializer
#     queryset = Payment.objects.all()
#
#     def perform_create(self, serializer):
#         pass
#        # serializer.save(is_active=True)



