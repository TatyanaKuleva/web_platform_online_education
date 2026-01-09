from rest_framework.test import APITestCase, APIClient, force_authenticate
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from materials.models import Course, Lesson, CourseSubscription

User = get_user_model()


class LessonCRUDTestCase(APITestCase):

    def setUp(self):
        self.client = APIClient()

        self.moderator_group, _ = Group.objects.get_or_create(name="moderators")

        self.owner = User.objects.create_user(email="user@yandex.com", password="password")

        self.moderator = User.objects.create_user(email="moderator@yandex.com", password="password")
        self.moderator.groups.add(self.moderator_group)

        self.other_user = User.objects.create_user(email="other@yandex.com", password="password")

        self.lesson = Lesson.objects.create(
            title="Начальный урок", video_url="https://youtube.com/watch?v=123", owner=self.owner
        )

        self.list_url = reverse("materials:lessons_list")
        self.create_url = reverse("materials:lessons_create")
        self.detail_url = reverse("materials:lessons_retrieve", args=[self.lesson.id])
        self.update_url = reverse("materials:lessons_update", args=[self.lesson.id])
        self.delete_url = reverse("materials:lessons_delete", args=[self.lesson.id])

    def test_lesson_create(self):
        """Проверка создания: модератор не может, обычный пользователь может"""
        data = {"title": "New Lesson", "video_url": "https://youtube.com/watch?v=test"}

        self.client.force_authenticate(user=self.moderator)
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.other_user)
        response = self.client.post(self.create_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_lesson_list(self):
        """Проверка списка: модератор видит всё, владелец — только своё"""
        Lesson.objects.create(
            title="Other Lesson", video_url="https://youtube.com/watch?v=test1", owner=self.other_user
        )

        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data.get("results", [])), 2)

        self.client.force_authenticate(user=self.owner)
        response = self.client.get(self.list_url)
        self.assertEqual(len(response.data.get("results", [])), 1)

    def test_lesson_retrieve(self):
        """Проверка просмотра: владелец и модератор могут, другие — нет"""

        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.client.force_authenticate(user=self.other_user)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_lesson_update(self):
        """Проверка обновления: модератор и владелец могут"""
        data = {"title": "Updated Title"}

        self.client.force_authenticate(user=self.moderator)
        response = self.client.patch(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.owner)
        response = self.client.patch(self.update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_lesson_delete(self):
        """Проверка удаления: владелец может, модератор — нет"""

        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.owner)
        response = self.client.delete(self.delete_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class CourseSubscriptionViewTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="user@example.com", password="password")
        self.course = Course.objects.create(title="Test Course")

        self.url = reverse("materials:course_subscribe")
        self.client.force_authenticate(user=self.user)

    def test_subscribe_success(self):
        data = {"user_id": self.user.id, "course_id": self.course.id, "action": "subscribe"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["detail"], "Подписка успешно добавлена")
        self.assertTrue(CourseSubscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscribe_already_exists(self):
        CourseSubscription.objects.create(user=self.user, course=self.course)
        data = {"user_id": self.user.id, "course_id": self.course.id, "action": "subscribe"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Подписка уже существует")

    def test_unsubscribe_success(self):
        CourseSubscription.objects.create(user=self.user, course=self.course)
        data = {"user_id": self.user.id, "course_id": self.course.id, "action": "unsubscribe"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["detail"], "Подписка успешно удалена")
        self.assertFalse(CourseSubscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe_not_found(self):
        data = {"user_id": self.user.id, "course_id": self.course.id, "action": "unsubscribe"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data["detail"], "Подписка не найдена")

    def test_missing_parameters(self):
        response = self.client.post(self.url, {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("user_id, course_id и action обязательны", response.data["detail"])

    def test_invalid_action(self):
        data = {"user_id": self.user.id, "course_id": self.course.id, "action": "invalid_action"}
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Неверное действие", response.data["detail"])
