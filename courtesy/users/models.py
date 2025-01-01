from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from pytils.translit import slugify as pytils_slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

# Кастомный менеджер для модели Account
class AccountManager(BaseUserManager):
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        if username is None:  # Если username не передан
            username = ""  # Устанавливаем пустым, чтобы не нарушать ограничения
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(username, email, password, **extra_fields)


# Модель Account
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
        # Если это новый пользователь (первое сохранение) и username не задан
        if not self.username:
            super().save(*args, **kwargs)  # Сначала сохранить, чтобы id был доступен
            self.username = str(self.id)  # Установить username равным id
        super().save(*args, **kwargs)  # Сохранить еще раз с обновленным username

    def __str__(self):
        full_name = f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()
        return full_name


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Слаг", blank=True, editable=False)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:  # Генерация слага только если он отсутствует
            self.slug = pytils_slugify(self.name)

        super().save(*args, **kwargs)

    def clean(self):
        if len(self.description) > 1000:
            raise ValidationError("Описание не может быть длиннее 1000 символов.")


class Specialist(models.Model):
    # Поле для фото, можно указать, куда сохранять файлы
    photo = models.ImageField(upload_to='specialists/photos/', blank=True, null=True, verbose_name="Фото")

    last_name = models.CharField(max_length=40, verbose_name="Фамилия")
    first_name = models.CharField(max_length=40, verbose_name="Имя")
    middle_name = models.CharField(max_length=40, blank=True, null=True, verbose_name="Отчество")

    slug = models.SlugField(max_length=50, unique=True, verbose_name="Слаг", blank=True, editable=False)

    speciality = models.CharField(max_length=200, verbose_name="Специальность")

    # Поле с ForeignKey для связи с моделью категории
    category = models.ForeignKey(
        'Category',  # Ссылка на модель категорий
        on_delete=models.SET_NULL,  # Удаляем специалиста, если удалена категория
        blank=True,
        null=True,
        verbose_name="Категория",
        related_name="specialists"
    )
    experience = models.CharField(max_length=25, verbose_name="Стаж работы")
    dop_info = models.TextField(verbose_name="Дополнительная информация", blank=True)

    class Meta:
        verbose_name = "Специалист"
        verbose_name_plural = "Специалисты"

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.middle_name or ''}".strip()

    def save(self, *args, **kwargs):
        # Генерация слага
        if not self.slug:
            fio = f"{self.last_name} {self.first_name[0]}. {self.middle_name[0] if self.middle_name else ''}"
            self.slug = pytils_slugify(fio.strip())

        super().save(*args, **kwargs)


class Service(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name="Название")
    # Поле с ForeignKey для связи с моделью категории
    category = models.ForeignKey(
        'Category',  # Ссылка на модель категорий
        on_delete=models.SET_NULL,  # Удаляем специалиста, если удалена категория
        blank=True,
        null=True,
        verbose_name="Категория",
        related_name="services"
    )
    description = models.TextField(verbose_name="Описание")
    link = models.CharField(max_length=200, blank=True, null=True, verbose_name="Ссылка")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Слаг", blank=True, editable=False)
    price = models.DecimalField(
        max_digits=10,  # Максимальная длина числа (включая запятую)
        decimal_places=2,  # Количество знаков после запятой
        default=Decimal('0.00'),
        verbose_name="Цена"
    )
    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:  # Генерация слага только если он отсутствует
            a = str(self.name) + " " + str(self.category)
            self.slug = pytils_slugify(a)

        super().save(*args, **kwargs)

    def clean(self):
        if len(self.description) > 1000:
            raise ValidationError("Описание не может быть длиннее 1000 символов.")


class News(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")  # Поле для названия
    main_image = models.ImageField(upload_to='news_images/', verbose_name="Главное фото")  # Поле для фото
    content = models.TextField(verbose_name="Содержимое")  # Поле для текста новости
    published_date = models.DateField(verbose_name="Дата публикации")  # Поле для даты
    slug = models.SlugField(max_length=255, unique=True, blank=True, verbose_name="Слаг")

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-published_date']  # Сортировка по убыванию даты публикации

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:  # Генерация слага только если он отсутствует
            self.slug = pytils_slugify(self.title)

        super().save(*args, **kwargs)


class Talon(models.Model):
    user = models.ForeignKey(
        'Account',  # Связь с моделью Account
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="talons"
    )
    date = models.DateField(verbose_name="Дата приёма")
    cabinet = models.CharField(max_length=20, verbose_name="Кабинет")
    doctor = models.ForeignKey(
        'Specialist',  # Связь с моделью Specialist
        on_delete=models.SET_NULL,
        verbose_name="Врач",
        related_name="talons",
        null=True
    )
    time = models.TimeField(verbose_name="Время приёма")  # Используем TimeField для времени
    service = models.ForeignKey(
        'Service',  # Связь с моделью Service
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
        # Отображаем пользователя, услугу и дату приёма
        return f'{self.user} - {self.service} ({self.date})'


class Review(models.Model):
    user = models.ForeignKey(
        'Account',  # Связь с моделью Account
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Пользователь",
        related_name="reviews"
    )
    rating = models.FloatField(
        verbose_name="Оценка",
        validators=[
            MinValueValidator(0.0, "Оценка не может быть меньше 0."),
            MaxValueValidator(5.0, "Оценка не может быть больше 5.")
        ]
    )
    content = models.TextField(verbose_name="Содержимое", blank=True)

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        ordering = ['-id']  # Последние отзывы вверху

    def __str__(self):
        # Возвращаем сокращённое ФИО и оценку
        return f"{self.user} - {self.rating}/5"

    def get_user_short_name(self):
        """Возвращает сокращённое ФИО пользователя."""
        if self.user:
            return f"{self.user.last_name} {self.user.first_name[0]}. {self.user.middle_name[0] if self.user.middle_name else ''}".strip()
        return "Аноним"


class SpecialistService(models.Model):
    specialist = models.ForeignKey(
        'Specialist',  # Ссылка на модель Specialist
        on_delete=models.CASCADE,
        verbose_name="Специалист",
        related_name="services"
    )
    service = models.ForeignKey(
        'Service',  # Ссылка на модель Service
        on_delete=models.CASCADE,
        verbose_name="Услуга",
        related_name="specialists"
    )

    class Meta:
        verbose_name = "Связь специалиста и услуги"
        verbose_name_plural = "Связи специалистов и услуг"
        unique_together = ('specialist', 'service')  # Уникальная пара "специалист-услуга"

    def __str__(self):
        return f"{self.specialist} - {self.service}"

    def specialist_category(self):
        return self.specialist.category.name  # Вывод категории специалиста

    specialist_category.admin_order_field = 'specialist__category'  # Для сортировки по категории
    specialist_category.short_description = 'Категория специалиста'  # Заголовок для админки