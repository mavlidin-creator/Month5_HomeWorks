from celery import shared_task
from django.core.mail import send_mail
import datetime , time


@shared_task
def long_task(x, y):
    time.sleep(5)
    return x + y

def print_current_time():
    now = datetime.datetime.now()
    print(f"Текущее время: {now}")


@shared_task
def send_welcome_email(to_email):
    send_mail(
        "Добро пожаловать!",
        "Спасибо за регистрацию на нашем сайте 🎉",
        "your_email@gmail.com",   
        [to_email],              
        fail_silently=False,
    )

