from datetime import date
from rest_framework.exceptions import ValidationError

def validate_user_is_adult(user):
    
    if not user.birthday:
        raise ValidationError("Дата рождения обязательна для создания продукта.")

    today = date.today()
    age = today.year - user.birthday.year - (
        (today.month, today.day) < (user.birthday.month, user.birthday.day)
    )

    if age < 18:
        raise ValidationError("Вам должно быть 18 лет, чтобы создать продукт.")
