from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, status, viewsets
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from materials.models import Course
from users.models import Payment, User
from users.permissions import IsUserOwner

from .serializers import (PaymentCreateSerializer, UserCreateSerializer, UserPrivateSerializer,
                          UserPublicSerializer)
from .services import create_stripe_price, create_stripe_product, create_stripe_session, get_stripe_session_status


@method_decorator(
    name="list",
    decorator=swagger_auto_schema(
        operation_description="Список пользователей (приватные данные)",
        responses={200: UserPrivateSerializer(many=True)},
    ),
)
@method_decorator(
    name="retrieve",
    decorator=swagger_auto_schema(
        operation_description="Просмотр профиля. Если это ваш профиль — данных больше.",
        responses={200: UserPrivateSerializer(), 203: UserPublicSerializer()},
    ),
)
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
        responses={201: UserCreateSerializer(), 400: "Ошибка валидации"},
    )
    def perform_create(self, serializer):
        serializer.save(is_active=True)


class CreatePaymentView(generics.GenericAPIView):
    serializer_class = PaymentCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        course_id = serializer.validated_data["course_id"]
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            return Response({"detail": "Course not found."}, status=status.HTTP_404_NOT_FOUND)

        product = create_stripe_product(course.title)
        amount = course.price if (hasattr(course, "price") and course.price is not None) else 10
        print(amount)
        price = create_stripe_price(amount, product.id)
        session = create_stripe_session(price.id)

        payment = Payment.objects.create(
            user=request.user,
            course=course,
            amount=amount,
            stripe_session_id=session.id,
            payment_link=session.url,
            status="pending",
        )

        return Response(
            {
                "payment_id": payment.id,
                "payment_link": payment.payment_link,
                "status": payment.status,
            },
            status=status.HTTP_201_CREATED,
        )


class PaymentStatusView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, session_id, *args, **kwargs):
        try:
            payment = Payment.objects.get(stripe_session_id=session_id, user=request.user)
        except Payment.DoesNotExist:
            return Response({"detail": "Payment not found."}, status=status.HTTP_404_NOT_FOUND)

        session_data = get_stripe_session_status(session_id)
        status_payment = session_data.get("payment_status", "unknown")

        payment.status = status_payment
        payment.save()

        return Response(
            {
                "payment_id": payment.id,
                "status": payment.status,
                "payment_link": payment.payment_link,
                "customer_email": session_data.get("customer_details", {}).get("email"),
            }
        )
