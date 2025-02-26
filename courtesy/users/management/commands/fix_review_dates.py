from django.core.management.base import BaseCommand
from django.utils.timezone import now
from users.models import Review

class Command(BaseCommand):
    help = "Заполняет пустые даты у отзывов текущей датой"

    def handle(self, *args, **kwargs):
        reviews = Review.objects.filter(date__isnull=True)
        count = reviews.count()

        for review in reviews:
            review.date = now().date()
            review.save()

        self.stdout.write(self.style.SUCCESS(f"Обновлено {count} отзывов."))
