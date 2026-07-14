from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta
from django.utils import timezone
from .models import CustomUser


@shared_task
def send_welcome_email(user_email):
    subject = 'Добро пожаловать!'
    message = 'Спасибо за регистрацию на нашем сайте.'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])
    return f"Письмо отправлено на {user_email}"


@shared_task
def delete_inactive_users():
    threshold = timezone.now() - timedelta(days=30)
    deleted = CustomUser.objects.filter(is_active=False, date_joined__lt=threshold).delete()
    return f"Удалено {deleted[0]} неактивных пользователей"


@shared_task
def send_daily_report():
    count = CustomUser.objects.count()
    subject = 'Ежедневный отчёт'
    message = f'Всего пользователей: {count}'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, ['admin@example.com'])
    return "Отчёт отправлен"