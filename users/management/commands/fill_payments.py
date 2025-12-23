import random
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from materials.models import Course, Lesson
from users.models import Payment

User = get_user_model()


class Command(BaseCommand):
    help = "Заполняет таблицу Payment примерными данными"

    def handle(self, *args, **kwargs):
        users = User.objects.all()[:3]

        courses = list(Course.objects.all()[:3])
        lessons = list(Lesson.objects.all()[:3])

        payment_methods = ["cash", "bank_transfer"]

        for i in range(20):
            user = random.choice(users)
            if random.choice([True, False]) and courses:
                course = random.choice(courses)
                lesson = None
            elif lessons:
                lesson = random.choice(lessons)
                course = None
            else:
                course = None
                lesson = None

            amount = Decimal(random.randint(500, 5000))

            payment_method = random.choice(payment_methods)
            payment_date = timezone.now()

            payment = Payment.objects.create(
                user=user,
                payment_date=payment_date,
                course=course,
                lesson=lesson,
                amount=amount,
                payment_method=payment_method,
            )
            self.stdout.write(
                self.style.SUCCESS(f"Создан платеж #{payment.id} для пользователя {user.username} — сумма {amount}")
            )
