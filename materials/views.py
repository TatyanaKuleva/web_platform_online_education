from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from materials.models import Course, CourseSubscription, Lesson
from materials.pagination import CustomPagination
from materials.serializers import CourseDetailSerializer, CourseSerializer, LessonSerializer
from users.permissions import IsModerators, IsOwner

from .tasks import send_course_update_email

User = get_user_model()


class CourseViewSet(ModelViewSet):
    """
    API для управления курсами.
    """

    queryset = Course.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return CourseDetailSerializer
        return CourseSerializer

    def perform_create(self, serializer):
        course = serializer.save()
        course.owner = self.request.user
        course.save()

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = (~IsModerators,)
        elif self.action == "destroy":
            self.permission_classes = (~IsModerators | IsOwner,)
        # elif self.action in ["update", "retrieve", "list"]:
        #     self.permission_classes = (IsOwner,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return [permission() for permission in self.permission_classes]

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.groups.filter(name="moderators").exists():
    #         return Course.objects.all()
    #
    #     return Course.objects.filter(owner=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_update(self, serializer):
        course = serializer.save()
        subscribers = CourseSubscription.objects.filter(course=course).select_related("user")

        for subscription in subscribers:
            email = subscription.user.email
            title = course.title
            print(f"Отправка email: {email}, курс: {title}")  # Или используйте logging
            send_course_update_email.delay(email, title)
        # for subscription in subscribers:
        #     send_course_update_email.delay(subscription.user.email, course.title)


class LessonCreateApiView(CreateAPIView):
    """
    API создания урока.
    """

    serializer_class = LessonSerializer
    permission_classes = (~IsModerators, IsAuthenticated)

    def perform_create(self, serializer):
        lesson = serializer.save()
        lesson.owner = self.request.user
        lesson.save()


class LessonListApiView(ListAPIView):
    """
    Просмотр списка уроков в зависимости от наличия разрешения пользователя.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerators | IsOwner]
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderators").exists():
            return Lesson.objects.all()

        return Lesson.objects.filter(owner=user)


class LessonRetrieveApiView(RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsModerators | IsOwner)


class LessonDestroyApiView(DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = (IsAuthenticated, IsOwner | ~IsModerators)


class LessonUpdateApiView(UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = (IsAuthenticated, IsModerators | IsOwner)


class CourseSubscriptionView(APIView):
    @swagger_auto_schema(
        operation_description="Подписка или отписка пользователя на курс",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["user_id", "course_id", "action"],
            properties={
                "user_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID пользователя"),
                "course_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="ID курса"),
                "action": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Действие: 'subscribe' или 'unsubscribe'"
                ),
            },
        ),
        responses={
            status.HTTP_201_CREATED: openapi.Response("Подписка успешно добавлена"),
            status.HTTP_200_OK: openapi.Response("Подписка уже существует или успешно удалена"),
            status.HTTP_404_NOT_FOUND: openapi.Response("Подписка не найдена"),
            status.HTTP_400_BAD_REQUEST: openapi.Response("Ошибка запроса"),
        },
    )
    def post(self, request):
        user_id = request.data.get("user_id")
        course_id = request.data.get("course_id")
        action = request.data.get("action")

        if not all([user_id, course_id, action]):
            return Response({"detail": "user_id, course_id и action обязательны"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, pk=user_id)
        course = get_object_or_404(Course, pk=course_id)

        if action == "subscribe":
            subscription, created = CourseSubscription.objects.get_or_create(user=user, course=course)
            if created:
                return Response({"detail": "Подписка успешно добавлена"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": "Подписка уже существует"}, status=status.HTTP_200_OK)

        elif action == "unsubscribe":
            subscription = CourseSubscription.objects.filter(user=user, course=course).first()
            if subscription:
                subscription.delete()
                return Response({"detail": "Подписка успешно удалена"}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Подписка не найдена"}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response(
                {"detail": "Неверное действие. Используйте 'subscribe' или 'unsubscribe'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
