from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import courtesy.constant as const


# Create your views here.


def index(request):
    return render(request, "index.html")


def about(request):
    return render(request, "about.html")


def personal_view(request):
    # Проверяем, авторизован ли пользователь
    if not request.user.is_authenticated:
        return redirect('login')  # Имя маршрута логина
    # Поменять!!!!
    return render(request, 'login.html')  # Рендер личного кабинета


# Страница входа
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if email == const.ADMIN_NAME and password == const.ADMIN_PASSWORD:
            # Здесь вы можете установить пользователя как администратора
            return redirect('admin')  # Имя маршрута для страницы admin.html

        # Если учетные данные неверные, вы можете добавить сообщение об ошибке
        # context = {'error': 'Неверная электронная почта или пароль.'}
        # return render(request, 'login.html', context)

    return render(request, 'login.html')


def signup_view(request):
    return render(request, 'signup.html')
