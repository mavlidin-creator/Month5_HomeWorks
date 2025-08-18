import os
import requests
import jwt
from rest_framework.exceptions import AuthenticationFailed

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")


def get_google_user_info_by_code(code: str):
    """
    Обменивает authorization code на токены Google и возвращает информацию о пользователе.
    """
    if not code:
        raise AuthenticationFailed("Code обязателен")

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    r = requests.post(token_url, data=data)
    if r.status_code != 200:
        raise AuthenticationFailed("Неверный code")

    tokens = r.json()
    id_token = tokens.get("id_token")
    if not id_token:
        raise AuthenticationFailed("ID token не получен")

    try:
        user_info = jwt.decode(id_token, options={"verify_signature": False})
    except Exception:
        raise AuthenticationFailed("Неверный ID token")

    email = user_info.get("email")
    if not email:
        raise AuthenticationFailed("Email не найден в токене")

    return {
        "email": email,
        "first_name": user_info.get("given_name", ""),
        "last_name": user_info.get("family_name", ""),
    }
