from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, Category, Specialist


# Настройка админки для модели Account
class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone')
    list_filter = ('is_active', 'is_staff')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('last_name', 'first_name', 'middle_name', 'date_of_birth', 'phone', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2')
        }),
    )

    ordering = ('username',)

    # Переопределяем метод сохранения для хэширования паролей
    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('password') and not obj.pk:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Убрали slug из отображаемых колонок
    search_fields = ('name',)  # Поле поиска остается по имени
    exclude = ('slug',)  # Исключаем поле slug из формы


class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'speciality', 'category')
    list_filter = ('category', 'speciality')  # Фильтры по категориям и специальностям
    search_fields = ('last_name', 'first_name', 'middle_name', 'speciality')  # Поля для поиска
    ordering = ('last_name', 'first_name')  # Сортировка по фамилии и имени
    exclude = ('slug',)  # Исключаем поле slug из формы
    fieldsets = (
        (None, {
            'fields': ('photo', 'last_name', 'first_name', 'middle_name', 'speciality', 'category', 'dop_info')
        }),

    )
    # prepopulated_fields = {'slug': ('last_name', 'first_name', 'middle_name')}  # Генерация slug на основе ФИО


# Регистрация модели в админке
admin.site.register(Account, AccountAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Specialist, SpecialistAdmin)
