from datetime import datetime, date
from rest_framework.exceptions import ValidationError

def validate_user_age_from_token(request):
    """
    Проверка возраста пользователя по дате рождения из JWT-токена.
    """
    user = request.user
    birthday = None

    if hasattr(user, 'birthday') and user.birthday:
        birthday = user.birthday
    else:
        if hasattr(request, 'auth') and request.auth:
            birthday = request.auth.get("birthday")

    if not birthday:
        raise ValidationError("Дата рождения не указана в профиле.")

    if isinstance(birthday, str):
        birthday = datetime.strptime(birthday, "%Y-%m-%d").date()

    today = date.today()
    age = today.year - birthday.year - (
        (today.month, today.day) < (birthday.month, birthday.day)
    )

    if age < 18:
        raise ValidationError("Вам должно быть 18 лет, чтобы создать продукт.")
