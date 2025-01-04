from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account, Category, Specialist, Service, News, Talon, Review, SpecialistService, Address, Contacts

admin.site.site_header = "Администрирование Courtesy"  # Заголовок панели администратора
admin.site.site_title = "Администрирование Courtesy"  # Заголовок на вкладке браузера
admin.site.index_title = "Администрирование Courtesy"  # Текст на главной странице админки


# Настройка админки для модели Account
class AccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'middle_name', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name')
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
    list_display = ('last_name', 'first_name', 'middle_name', 'speciality', 'category', 'experience')
    list_filter = ('category', 'speciality')  # Фильтры по категориям и специальностям
    search_fields = ('last_name', 'first_name', 'middle_name', 'speciality')  # Поля для поиска
    ordering = ('last_name', 'first_name')  # Сортировка по фамилии и имени
    exclude = ('slug',)  # Исключаем поле slug из формы
    fieldsets = (
        (None, {
            'fields': (
                'photo', 'last_name', 'first_name', 'middle_name', 'speciality', 'category', 'experience', 'dop_info')
        }),

    )


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', "price", "description")  # Отображаемые поля в списке
    search_fields = ('name', 'category__name')  # Поля для поиска (включая название категории)
    list_filter = ('category',)  # Фильтрация по категории
    exclude = ('slug',)  # Исключаем поле slug из формы

    fieldsets = (
        (None, {
            "fields": ("name", "category", "price", "description", "link")
        }),
    )


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'main_image_preview')  # Отображение столбцов в списке
    search_fields = ('title', 'content')  # Поля для поиска
    list_filter = ('published_date',)  # Фильтр по дате публикации
    date_hierarchy = 'published_date'  # Навигация по датам
    fields = ('title', 'main_image', 'content', 'published_date')  # Поля в форме редактирования
    readonly_fields = ('main_image_preview',)  # Поле для предпросмотра изображения
    exclude = ('slug',)  # Исключаем поле slug из формы

    def main_image_preview(self, obj):
        """Отображение предпросмотра изображения в админке."""
        if obj.main_image:
            return f'<img src="{obj.main_image.url}" style="max-height: 100px;">'
        return "Нет изображения"

    main_image_preview.short_description = "Предпросмотр фото"
    main_image_preview.allow_tags = True


from django.contrib import admin


class TalonAdmin(admin.ModelAdmin):
    list_display = (
        'get_user_full_name',
        'date',
        'cabinet',
        'get_doctor_full_name',
        'time',
        'get_service_name',
    )
    list_filter = ('date', 'cabinet')
    search_fields = ('user__last_name', 'user__first_name', 'doctor__last_name', 'service__name')

    def get_user_full_name(self, obj):
        return f"{obj.user.last_name} {obj.user.first_name} {obj.user.middle_name or ''}".strip()

    get_user_full_name.short_description = "Пользователь"

    def get_doctor_full_name(self, obj):
        return f"{obj.doctor.last_name} {obj.doctor.first_name[0]}. {obj.doctor.middle_name[0] if obj.doctor.middle_name else ''}"

    get_doctor_full_name.short_description = "Врач"

    def get_service_name(self, obj):
        return obj.service.name

    get_service_name.short_description = "Услуга"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            # Фильтруем пользователей без статуса персонала
            kwargs["queryset"] = db_field.related_model.objects.filter(is_staff=False)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('get_user_short_name', 'rating', 'content_preview')  # Поля, отображаемые в списке
    list_filter = ('rating',)  # Фильтрация по оценке
    search_fields = ('user__last_name', 'user__first_name', 'content')  # Поиск по имени и содержимому
    readonly_fields = ('get_user_short_name',)  # Поле только для чтения
    fields = ('get_user_short_name', 'rating', 'content')  # Порядок полей в форме

    @admin.display(description="Пользователь")
    def get_user_short_name(self, obj):
        """Возвращает сокращённое ФИО пользователя."""
        return obj.get_user_short_name()

    @admin.display(description="Содержимое")
    def content_preview(self, obj):
        """Обрезка содержимого для краткого отображения."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content


class SpecialistServiceAdmin(admin.ModelAdmin):
    list_display = ('specialist', 'specialist_category', 'service')  # Отображение связей в списке
    search_fields = (
        'specialist__last_name', 'specialist__first_name',
        'service__name')  # Поиск по имени специалиста и названию услуги
    list_filter = ('specialist', 'service')  # Фильтры по специалистам и услугам

    def specialist_display(self, obj):
        # Отображение ФИО специалиста в удобном формате
        return f"{obj.specialist.last_name} {obj.specialist.first_name} {obj.specialist.middle_name or ''}".strip()

    specialist_display.short_description = "Специалист"  # Название колонки


class AddressAdmin(admin.ModelAdmin):
    list_display = ("address", "working_hours", "latitude", "longitude")
    search_fields = ("address",)
    list_filter = ("working_hours",)
    fieldsets = (
        (None, {
            "fields": ("address", "working_hours")
        }),
        ("Координаты", {
            "fields": ("latitude", "longitude"),
            "classes": ("collapse",),
        }),
    )


class ContactsAdmin(admin.ModelAdmin):
    list_display = ("person", "what_doing", "contact")
    search_fields = ("person", "what_doing", "contact")
    list_filter = ("person", "what_doing")
    fields = ("person", "contact", "what_doing")


# Регистрация модели в админке
admin.site.register(Account, AccountAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Specialist, SpecialistAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Talon, TalonAdmin)
admin.site.register(SpecialistService, SpecialistServiceAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Contacts, ContactsAdmin)
