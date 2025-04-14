from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_confirmation_email(user, code):
    subject = 'Код подтверждения регистрации Courtesy'

    # Генерация HTML содержимого письма
    html_message = render_to_string('email/confirmation_email.html', {
        'user': user,
        'code': code,
    })

    # Генерация текста письма (для случаев, когда HTML не поддерживается)
    plain_message = strip_tags(html_message)

    # Отправка письма
    send_mail(
        subject,
        plain_message,  # Текстовая версия письма
        'noreply@clinic-site.com',
        [user.email],
        html_message=html_message,  # HTML версия письма
        fail_silently=False,
    )
