from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import timedelta
from .models import Talon


@shared_task
def send_appointment_reminders():
    tomorrow = timezone.now().date() + timedelta(days=1)

    tomorrow_talons = Talon.objects.filter(date=tomorrow)

    for talon in tomorrow_talons:
        if talon.user.email:
            context = {
                'user': talon.user,
                'talon': talon,
                'date': talon.date.strftime('%d.%m.%Y'),
                'time': talon.time.strftime('%H:%M'),
            }

            message = render_to_string('emails/appointment_reminder.txt', context)
            html_message = render_to_string('emails/appointment_reminder.html', context)

            send_mail(
                subject=f'Напоминание о приеме {talon.date}',
                message=message,
                html_message=html_message,
                from_email='courtesy.clinic.email@gmail.com',
                recipient_list=[talon.user.email],
                fail_silently=False,
            )