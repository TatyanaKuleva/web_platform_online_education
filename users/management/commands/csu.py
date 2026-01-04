from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = "Создает суперпользователя"

    def handle(self, *args, **kwargs):
        user = User.objects.create(email="admin@admin.ru")
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.set_password("120152")
        user.save()
