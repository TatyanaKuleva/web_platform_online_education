from celery import shared_task
from config.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_course_update_email(user_email, course_title):
    subject = f"Обновление курса {course_title}"
    message = f"Здравствуйте! В курсе '{course_title}' появились обновления. Заходите и смотрите новости!"
    from_email = EMAIL_HOST_USER
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list)
    # print(subject, message, from_email, recipient_list)

