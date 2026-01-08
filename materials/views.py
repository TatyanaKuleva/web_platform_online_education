from rest_framework.generics import CreateAPIView, DestroyAPIView, ListAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status


from materials.models import Course, Lesson, CourseSubscription
from materials.pagination import CustomPagination
from materials.serializers import CourseDetailSerializer, CourseSerializer, LessonSerializer
from users.permissions import IsModerators, IsOwner
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

User = get_user_model()

class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if self.action is "retrieve":
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
        elif self.action in ["update", "retrieve", "list"]:
            self.permission_classes = (IsOwner,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="moderators").exists():
            return Course.objects.all()

        return Course.objects.filter(owner=user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class LessonCreateApiView(CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = (~IsModerators, IsAuthenticated)

    def perform_create(self, serializer):
        lesson = serializer.save()
        lesson.owner = self.request.user
        lesson.save()


class LessonListApiView(ListAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsModerators| IsOwner]
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

    def post(self, request):
        user_id = request.data.get('user_id')
        course_id = request.data.get('course_id')
        action = request.data.get('action')

        if not all([user_id, course_id, action]):
            return Response({"detail": "user_id, course_id и action обязательны"}, status=status.HTTP_400_BAD_REQUEST)

        user = get_object_or_404(User, pk=user_id)
        course = get_object_or_404(Course, pk=course_id)

        if action == 'subscribe':
            subscription, created = CourseSubscription.objects.get_or_create(user=user, course=course)
            if created:
                return Response({"detail": "Подписка успешно добавлена"}, status=status.HTTP_201_CREATED)
            else:
                return Response({"detail": "Подписка уже существует"}, status=status.HTTP_200_OK)

        elif action == 'unsubscribe':
            subscription = CourseSubscription.objects.filter(user=user, course=course).first()
            if subscription:
                subscription.delete()
                return Response({"detail": "Подписка успешно удалена"}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Подписка не найдена"}, status=status.HTTP_404_NOT_FOUND)

        else:
            return Response({"detail": "Неверное действие. Используйте 'subscribe' или 'unsubscribe'."},
                            status=status.HTTP_400_BAD_REQUEST)

