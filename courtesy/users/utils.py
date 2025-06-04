from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_confirmation_email(user, code):
    subject = 'Код подтверждения регистрации Courtesy'

    html_message = render_to_string('email/confirmation_email.html', {
        'user': user,
        'code': code,
    })

    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        'noreply@clinic-site.com',
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )
