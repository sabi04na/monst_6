from datetime import date
from rest_framework.exceptions import ValidationError

def validate_age_from_token(request):
    """
    Проверяет возраст пользователя по дате рождения из токена.
    """
    user = request.user

    if not user or not user.is_authenticated:
        raise ValidationError("Пользователь не аутентифицирован.")

    birthdate = getattr(user, 'birthdate', None)

    if not birthdate:
        raise ValidationError("Укажите дату рождения, чтобы создать продукт.")

    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))

    if age < 18:
        raise ValidationError("Вам должно быть 18 лет, чтобы создать продукт.")

    return True