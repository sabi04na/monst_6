from celery import shared_task
from django.core.mail import send_mail
from datetime import timedelta
from django.utils import timezone
from .models import CustomUser


@shared_task
def send_welcome_email(user_email):
    send_mail(
        subject='Добро пожаловать!',
        message='Вы успешно зарегистрировались.',
        from_email='admin@example.com',
        recipient_list=[user_email],
        fail_silently=False,
    )
    return f"Письмо отправлено {user_email}"


@shared_task
def delete_inactive_users():
    threshold_date = timezone.now() - timedelta(days=30)
    deleted_count, _ = CustomUser.objects.filter(is_active=False, date_joined__lt=threshold_date).delete()
    return f"Удалено {deleted_count} неактивных пользователей"


@shared_task
def send_daily_report():
    return "Ежедневный отчёт отправлен!"