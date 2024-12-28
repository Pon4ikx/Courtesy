from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib import admin

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


