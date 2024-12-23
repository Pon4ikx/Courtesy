from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account


# Создаём кастомную форму для пользователя (если нужно)
# from django import forms
# class AccountChangeForm(forms.ModelForm):
#     class Meta:
#         model = Account
#         fields = '__all__'

# # Также можно создать форму для создания пользователя
# class AccountCreationForm(forms.ModelForm):
#     class Meta:
#         model = Account
#         fields = ('username', 'email', 'phone', 'password')

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


# Регистрация модели в админке
admin.site.register(Account, AccountAdmin)
