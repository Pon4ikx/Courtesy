from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from pytils.translit import slugify as pytils_slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone
import requests
from urllib.parse import quote
from django.utils.timezone import localdate
from django.conf import settings



class AccountManager(BaseUserManager):
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        if username is None:
            username = ""
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)


class Account(AbstractUser):
    last_name = models.CharField(max_length=40, verbose_name="Фамилия")
    first_name = models.CharField(max_length=40, verbose_name="Имя")
    middle_name = models.CharField(max_length=40, blank=True, null=True, verbose_name="Отчество")
    date_of_birth = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name="Телефон")
    email = models.EmailField(unique=True, verbose_name="Почта")

    objects = AccountManager()

    class Meta:
        verbose_name = "Аккаунт"
        verbose_name_plural = "Аккаунты"

    def save(self, *args, **kwargs):

        if not self.username:
            super().save(*args, **kwargs)
            self.username = str(self.id)
        super().save(*args, **kwargs)

    def __str__(self):
        full_name = f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()
        return full_name


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Слаг", blank=True, editable=False)

    class Meta:
        verbose_name = "Направление"
        verbose_name_plural = "Направления"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = pytils_slugify(self.name)

        super().save(*args, **kwargs)

    def clean(self):
        if len(self.description) > 1000:
            raise ValidationError("Описание не может быть длиннее 1000 символов.")


class Specialist(models.Model):

    photo = models.ImageField(upload_to='specialists/photos/', blank=True, null=True, verbose_name="Фото")

    last_name = models.CharField(max_length=40, verbose_name="Фамилия")
    first_name = models.CharField(max_length=40, verbose_name="Имя")
    middle_name = models.CharField(max_length=40, blank=True, null=True, verbose_name="Отчество")

    slug = models.SlugField(max_length=50, unique=True, verbose_name="Слаг", blank=True, editable=False)

    speciality = models.CharField(max_length=200, verbose_name="Специальность")


    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Направление",
        related_name="specialists"
    )
    experience = models.CharField(max_length=25, verbose_name="Стаж работы")
    dop_info = models.TextField(verbose_name="Дополнительная информация", blank=True)
    display_on_main = models.BooleanField(default=False, verbose_name="Отображать на главной странице")

    appointment_duration = models.PositiveIntegerField(
        default=20,
        verbose_name="Длительность приёма (в минутах)"
    )

    class Meta:
        verbose_name = "Специалист"
        verbose_name_plural = "Специалисты"

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()

    def save(self, *args, **kwargs):

        if not self.slug:
            fio = f"{self.last_name} {self.first_name[0]}. {self.middle_name[0] if self.middle_name else ''}"
            self.slug = pytils_slugify(fio.strip())

        super().save(*args, **kwargs)


class Service(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Название")

    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Направление",
        related_name="services"
    )
    description = models.TextField(verbose_name="Описание")
    link = models.CharField(max_length=200, blank=True, null=True, verbose_name="Ссылка")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Слаг", blank=True, editable=False)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Цена"
    )

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        if not self.slug:
            a = str(self.name) + " " + str(self.category)
            self.slug = pytils_slugify(a)

        super().save(*args, **kwargs)

    def clean(self):
        if len(self.description) > 1000:
            raise ValidationError("Описание не может быть длиннее 1000 символов.")


class News(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name="Название")
    main_image = models.ImageField(upload_to='news_images/', verbose_name="Главное фото")
    content = models.TextField(verbose_name="Содержимое")
    published_date = models.DateField(verbose_name="Дата публикации")
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Слаг")

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    @property
    def is_new(self):
        """Возвращает True, если новость была опубликована менее недели назад."""
        return self.published_date >= (timezone.now().date() - timedelta(days=7))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = pytils_slugify(self.title)

        super().save(*args, **kwargs)


class Talon(models.Model):
    user = models.ForeignKey(
        'Account',
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="talons"
    )
    date = models.DateField(verbose_name="Дата приёма")
    cabinet = models.CharField(max_length=20, verbose_name="Кабинет")
    doctor = models.ForeignKey(
        'Specialist',
        on_delete=models.SET_NULL,
        verbose_name="Врач",
        related_name="talons",
        null=True
    )
    time = models.TimeField(verbose_name="Время приёма")
    service = models.ForeignKey(
        'Service',
        on_delete=models.SET_NULL,
        verbose_name="Услуга",
        related_name="talons",
        null=True
    )
    dop_info = models.TextField(verbose_name="Дополнительная информация", blank=True)

    class Meta:
        verbose_name = "Талон"
        verbose_name_plural = "Талоны"

    def __str__(self):

        return f'{self.user} - {self.service} ({self.date})'


class Review(models.Model):
    user = models.ForeignKey(
        'Account',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь",
        related_name="reviews"
    )
    rating = models.IntegerField(
        verbose_name="Оценка",
        validators=[
            MinValueValidator(0, "Оценка не может быть меньше 0."),
            MaxValueValidator(5, "Оценка не может быть больше 5.")
        ]
    )
    date = models.DateField(verbose_name="Дата", default=localdate)
    content = models.TextField(verbose_name="Содержимое", blank=True)
    confirmed = models.BooleanField(verbose_name="Проверено", default=False)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-id']

    def __str__(self):

        return f"{self.user} - {self.rating}/5"

    def get_user_short_name(self):
        """Возвращает сокращённое ФИО пользователя."""
        if self.user:
            return f"{self.user.last_name} {self.user.first_name[0]}. {self.user.middle_name[0] if self.user.middle_name else ''}".strip()
        return "Аноним"

    def clean(self):
        """Проверка, что дата не в будущем."""
        if self.date > localdate():
            raise ValidationError({"date": "Дата не может быть в будущем."})


class SpecialistService(models.Model):
    specialist = models.ForeignKey(
        'Specialist',
        on_delete=models.CASCADE,
        verbose_name="Специалист",
        related_name="services"
    )
    service = models.ForeignKey(
        'Service',
        on_delete=models.CASCADE,
        verbose_name="Услуга",
        related_name="specialists"
    )

    class Meta:
        verbose_name = "Связь специалиста и услуги"
        verbose_name_plural = "Связи специалистов и услуг"
        unique_together = ('specialist', 'service')

    def __str__(self):
        return f"{self.specialist} - {self.service}"


class Address(models.Model):
    address = models.CharField(
        max_length=255,
        verbose_name="Адрес",
        unique=True,
        help_text="Пример: ул. (Название улицы или проспекта(пр.)), (Номер дома), Город<br>" +
                  "Если в адресе проспект, то надо писать полностью: проспект (Название)"
    )
    working_hours = models.CharField(max_length=100, verbose_name="Время работы", blank=True,
                                     null=True)

    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, verbose_name="Широта", blank=True, null=True
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, verbose_name="Долгота", blank=True, null=True
    )

    class Meta:
        verbose_name = "Адрес"
        verbose_name_plural = "Адреса"

    def save(self, *args, **kwargs):

        if not self.latitude or not self.longitude:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': quote(self.address),
                'format': 'json',
                'addressdetails': 1,
                'limit': 1,
                'accept-language': 'ru'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'
            }
            response = requests.get(url, params=params, headers=headers)


            if response.status_code == 200:
                data = response.json()

                print(f"Запрос: {self.address}")
                print(f"Ответ: {data}")

                if data:
                    self.latitude = data[0].get('lat', None)
                    self.longitude = data[0].get('lon', None)
                else:
                    print("Нет данных для данного адреса.")
            else:
                print(f"Ошибка: {response.status_code} - {response.text}")


        super().save(*args, **kwargs)

    def __str__(self):
        return self.address


# class Address(models.Model):
#     address = models.CharField(
#         max_length=255,
#         verbose_name="Адрес",
#         unique=True,
#         help_text="Пример: ул. (Название улицы или проспекта(пр.)), (Номер дома), Город<br>" +
#                   "Если в адресе проспект, то надо писать полностью: проспект (Название)"
#     )
#     working_hours = models.CharField(max_length=100, verbose_name="Время работы", blank=True, null=True)
#     latitude = models.DecimalField(
#         max_digits=9, decimal_places=6, verbose_name="Широта", blank=True, null=True
#     )
#     longitude = models.DecimalField(
#         max_digits=9, decimal_places=6, verbose_name="Долгота", blank=True, null=True
#     )
#
#     class Meta:
#         verbose_name = "Адрес"
#         verbose_name_plural = "Адреса"
#
#     def save(self, *args, **kwargs):
#         if not self.latitude or not self.longitude:
#             api_key = '1f94f378144d44938b3c2997a4fe6544'
#             url = "https://api.geoapify.com/v1/geocode/search"
#             params = {
#                 'text': self.address,
#                 'apiKey': api_key,
#                 'format': 'json',
#                 'limit': 1,
#                 'lang': 'ru'
#             }
#             response = requests.get(url, params=params)
#             if response.status_code == 200:
#                 data = response.json()
#                 if data and 'features' in data and data['features']:
#                     location = data['features'][0]['geometry']['coordinates']
#                     self.longitude = location[0]
#                     self.latitude = location[1]
#                 else:
#                     print("Нет данных для адреса:", self.address)
#             else:
#                 print("Ошибка API:", response.status_code, response.text)
#         super().save(*args, **kwargs)
#
#     def __str__(self):
#         return self.address


class Contacts(models.Model):
    contact = models.CharField(max_length=100, unique=True, verbose_name="Данные для связи")
    person = models.CharField(max_length=100, verbose_name="Человек для связи")
    what_doing = models.CharField(max_length=100, default="", verbose_name="Занятость")

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"

    def __str__(self):
        return f'{self.contact} - {self.person}'


class EmailConfirmationCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Code for {self.user.email}: {self.code}"


class Cabinet(models.Model):
    number = models.CharField(max_length=10, unique=True, verbose_name="Номер кабинета")
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, verbose_name="Направление")

    class Meta:
        verbose_name = "Кабинет"
        verbose_name_plural = "Кабинеты"

    def __str__(self):
        return f"Кабинет №{self.number}"


class Schedule(models.Model):
    specialist = models.ForeignKey('Specialist', on_delete=models.CASCADE, verbose_name="Специалист")
    date = models.DateField(verbose_name="Дата")
    start_time = models.TimeField(verbose_name="Время начала", null=True)
    end_time = models.TimeField(verbose_name="Время окончания", null=True)
    cabinet = models.ForeignKey('Cabinet', on_delete=models.SET_NULL, null=True, verbose_name="Кабинет")
    is_day_off = models.BooleanField(default=False, verbose_name="Выходной")

    class Meta:
        verbose_name = "Расписание"
        verbose_name_plural = "Расписания"
        unique_together = ("specialist", "date")

    def __str__(self):
        return f"{self.specialist} – {self.date}"
