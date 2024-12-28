from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib import admin
from django.utils import timezone
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from pytils.translit import slugify as pytils_slugify


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
        return f"{self.username} ({self.email})"


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

    dop_info = models.TextField(verbose_name="Дополнительная информация", blank=True)

    class Meta:
        verbose_name = "Специалист"
        verbose_name_plural = "Специалисты"

    def __str__(self):
        return f"{self.last_name} {self.first_name}. {self.middle_name or ''}".strip()

    def save(self, *args, **kwargs):
        # Генерация слага
        if not self.slug:
            fio = f"{self.last_name} {self.first_name[0]}. {self.middle_name[0] if self.middle_name else ''}"
            self.slug = pytils_slugify(fio.strip())

        super().save(*args, **kwargs)
