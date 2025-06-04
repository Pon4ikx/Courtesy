from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import path
import os
from courtesy.settings import BASE_DIR
from .models import (Account, Category, Specialist, Service, News, Talon, Review, SpecialistService, Address, Contacts,
                     Cabinet, Schedule)

admin.site.site_header = "Администрирование Courtesy"  # Заголовок панели администратора
admin.site.site_title = "Администрирование Courtesy"  # Заголовок на вкладке браузера
admin.site.index_title = "Администрирование Courtesy"  # Текст на главной странице админки


class AccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'middle_name', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone', 'first_name', 'last_name', 'middle_name')
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

    def save_model(self, request, obj, form, change):
        if form.cleaned_data.get('password') and not obj.pk:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    exclude = ('slug',)


class SpecialistAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'middle_name', 'speciality', 'category', 'experience', "display_on_main",
                    "appointment_duration")
    list_filter = ('category', 'speciality', "appointment_duration")
    search_fields = ('last_name', 'first_name', 'middle_name', 'speciality', 'display_on_main')
    ordering = ('last_name', 'first_name', 'display_on_main')
    exclude = ('slug',)
    fieldsets = (
        (None, {
            'fields': (
                'photo', 'last_name', 'first_name', 'middle_name',
                'speciality', 'category', "appointment_duration", 'experience', 'dop_info',
                'display_on_main')
        }),

    )


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', "price", "description")
    search_fields = ('name', 'category__name')
    list_filter = ('category',)
    exclude = ('slug',)

    fieldsets = (
        (None, {
            "fields": ("name", "category", "price", "description", "link")
        }),
    )


class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'published_date', 'main_image_preview')
    search_fields = ('title', 'content', 'published_date')
    list_filter = ('published_date',)
    date_hierarchy = 'published_date'
    fields = ('title', 'main_image', 'content', 'published_date')
    readonly_fields = ('main_image_preview',)
    exclude = ('slug',)

    def main_image_preview(self, obj):
        """Отображение предпросмотра изображения в админке."""
        if obj.main_image:
            return f'<img src="{obj.main_image.url}" style="max-height: 100px;">'
        return "Нет изображения"

    main_image_preview.short_description = "Предпросмотр фото"
    main_image_preview.allow_tags = True


class TalonAdmin(admin.ModelAdmin):
    list_display = (
        'get_doctor_full_name',
        'get_user_full_name',
        'date',
        'cabinet',
        'time',
        'get_service_name',
    )
    list_filter = ('date', 'cabinet')
    search_fields = ('user__last_name', 'user__first_name', 'doctor__last_name', 'service__name')
    date_hierarchy = 'date'

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
        if db_field.name == "service" and 'doctor' in request.GET:
            doctor_id = request.GET.get('doctor')
            if doctor_id:
                service_ids = SpecialistService.objects.filter(specialist_id=doctor_id).values_list('service_id',
                                                                                                    flat=True)
                kwargs['queryset'] = Service.objects.filter(id__in=service_ids)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            (None, {
                'fields': ('doctor', 'user', 'service', 'date', 'time', 'cabinet', 'dop_info'),
            }),
        ]
        return fieldsets

    class Media:
        js = ('js/talon_filter.js',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('get_user_short_name', 'rating', 'content_preview', 'date', 'confirmed')
    list_filter = ('rating', 'date', 'confirmed')
    search_fields = ('user__last_name', 'user__first_name', 'content', 'date')
    readonly_fields = ('get_user_short_name',)
    fields = ('confirmed', 'get_user_short_name', 'rating', 'date', 'content')
    date_hierarchy = 'date'

    @admin.display(description="Пользователь")
    def get_user_short_name(self, obj):
        """Возвращает сокращённое ФИО пользователя."""
        return obj.get_user_short_name()

    @admin.display(description="Содержимое")
    def content_preview(self, obj):
        """Обрезка содержимого для краткого отображения."""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content


CATEGORY_FILE = os.path.join(BASE_DIR, 'data', 'category_id.txt')


def get_category_id():
    if os.path.exists(CATEGORY_FILE):
        with open(CATEGORY_FILE, 'r') as file:
            category_id = file.read().strip()
            return category_id
    return None


def set_category_id(category_id):
    with open(CATEGORY_FILE, 'w') as file:
        file.write(str(category_id))


class SpecialistServiceAdmin(admin.ModelAdmin):
    list_display = ('specialist', 'service', 'specialist_category')
    search_fields = ('specialist__first_name', 'specialist__last_name', 'service__name',)
    list_filter = ('specialist', 'specialist__category',)

    def specialist_category(self, obj):
        return obj.specialist.category.name

    specialist_category.short_description = 'Направление специалиста'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        category_id = get_category_id()
        if db_field.name == "specialist" and category_id:
            kwargs['queryset'] = Specialist.objects.filter(category_id=category_id)
        elif db_field.name == "service" and category_id:
            kwargs['queryset'] = Service.objects.filter(category_id=category_id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('apply_filter/', self.admin_site.admin_view(self.apply_filter), name='apply_filter'),
        ]
        return custom_urls + urls

    def apply_filter(self, request):
        category_id = request.GET.get('category')
        if category_id:
            set_category_id(category_id)
            return HttpResponseRedirect(f'/admin/users/specialistservice/add/?category={category_id}')
        return HttpResponseRedirect('/admin/users/specialistservice/add/')

    def add_view(self, request, form_url='', extra_context=None):

        category_id = request.GET.get('category')

        if category_id:
            set_category_id(category_id)

        category_id_from_file = get_category_id()

        categories = Category.objects.all()

        filter_message = ""
        if category_id_from_file and category_id_from_file.isdigit():
            category_id_from_file = int(category_id_from_file)
            category = categories.filter(id=category_id_from_file).first()
            if category:
                filter_message = f"Фильтрация по направлению: {category.name}"

        extra_context = extra_context or {}
        extra_context['categories'] = categories
        extra_context['category_id'] = category_id_from_file
        extra_context['filter_message'] = filter_message

        response = super().add_view(request, form_url, extra_context=extra_context)

        return response

    def response_add(self, request, obj, post_url_continue=None):
        category_id = request.POST.get('category')
        if category_id:
            set_category_id(category_id)
        return super().response_add(request, obj, post_url_continue)


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


class CabinetAdmin(admin.ModelAdmin):
    list_display = ('number', 'category')
    list_filter = ('category',)
    search_fields = ('number',)
    ordering = ('number',)


class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('specialist', 'cabinet', 'date', 'start_time', 'end_time')
    search_fields = ('specialist__name', 'cabinet__number', 'date',)
    list_filter = ('specialist', 'date',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('apply_specialist_filter/', self.admin_site.admin_view(self.apply_specialist_filter),
                 name='apply_specialist_filter'),
        ]
        return custom_urls + urls

    def apply_specialist_filter(self, request):
        specialist_id = request.GET.get('specialist')
        if specialist_id:
            request.session['specialist_id'] = specialist_id
            return HttpResponseRedirect(f'/admin/users/schedule/add/?specialist={specialist_id}')
        return HttpResponseRedirect('/admin/users/schedule/add/')

    def add_view(self, request, form_url='', extra_context=None):
        specialist_id = request.GET.get('specialist')
        if specialist_id:
            request.session['specialist_id'] = specialist_id

        specialist_id = request.session.get('specialist_id')
        cabinets = Cabinet.objects.all()
        specialists = Specialist.objects.all()

        if specialist_id:
            specialist = Specialist.objects.filter(id=specialist_id).first()
            if specialist:
                cabinets = Cabinet.objects.filter(category=specialist.category)
                filter_message = f"Фильтрация по направлению: {specialist.category.name}"
            else:
                filter_message = ""
        else:
            filter_message = ""

        extra_context = extra_context or {}
        extra_context['specialist_id'] = specialist_id
        extra_context['cabinets'] = cabinets
        extra_context['specialists'] = specialists
        extra_context['filter_message'] = filter_message

        return super().add_view(request, form_url, extra_context=extra_context)

    def get_specialist_category(self, specialist_id):
        """ Получаем категорию специалиста по его id """
        if specialist_id:
            specialist = Specialist.objects.filter(id=specialist_id).first()
            if specialist:
                return specialist.category.id
        return None

admin.site.register(Account, AccountAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Specialist, SpecialistAdmin)
admin.site.register(Service, ServiceAdmin)
admin.site.register(News, NewsAdmin)
admin.site.register(Talon, TalonAdmin)
admin.site.register(SpecialistService, SpecialistServiceAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(Contacts, ContactsAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Cabinet, CabinetAdmin)
admin.site.register(Schedule, ScheduleAdmin)
